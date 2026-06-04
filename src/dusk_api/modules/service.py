import inspect
from functools import wraps
from typing import Any

from dusk_api.contracts import ServiceDecoratorConfig, ServiceDecoratorRule, ServiceMapperContext
from dusk_api.tokens import SERVICE_DECORATOR_PHASE, SERVICE_DECORATOR_SAFE_ERROR_MESSAGE, SERVICE_DECORATOR_TRANSFORM_ERROR_CODE


class ServiceDecoratorTransformError(ValueError):
    def __init__(self, phase: str, target: str, message: str) -> None:
        super().__init__(message)
        self.name = "ServiceDecoratorTransformError"
        self.code = SERVICE_DECORATOR_TRANSFORM_ERROR_CODE
        self.phase = phase
        self.target = target


class ServiceDecorator:
    def __init__(self, service: object, config: ServiceDecoratorConfig) -> None:
        self._service = service
        self._service_name = config.service_name or "service"
        self._rules = config.rules

    def decorate(self) -> object:
        class Proxy:
            def __init__(proxy_self, wrapped: object, owner: "ServiceDecorator") -> None:
                proxy_self._wrapped = wrapped
                proxy_self._owner = owner

            def __getattr__(proxy_self, item: str):
                member = getattr(proxy_self._wrapped, item)
                if not callable(member):
                    return member

                if inspect.iscoroutinefunction(member):
                    @wraps(member)
                    async def async_wrapped(*args, **kwargs):
                        mapped_args = await proxy_self._owner._map_call_args(list(args), item)
                        result = await member(*mapped_args, **kwargs)
                        return await proxy_self._owner._map_call_result(result, item)

                    return async_wrapped

                @wraps(member)
                def sync_wrapped(*args, **kwargs):
                    return member(*args, **kwargs)

                return sync_wrapped

        return Proxy(self._service, self)

    def _should_apply_rule(self, rule: ServiceDecoratorRule, method_name: str) -> bool:
        if not rule.methods:
            return True
        return method_name in rule.methods

    def _ensure_args_array(self, value: Any, context: ServiceMapperContext) -> list[Any]:
        if isinstance(value, list):
            return value
        raise ServiceDecoratorTransformError(
            phase=context.phase,
            target=f"{context.service_name}.{context.method_name}",
            message=SERVICE_DECORATOR_SAFE_ERROR_MESSAGE,
        )

    def _wrap_transform_error(self, error: Exception, context: ServiceMapperContext) -> ServiceDecoratorTransformError:
        if isinstance(error, ServiceDecoratorTransformError):
            return error
        return ServiceDecoratorTransformError(
            phase=context.phase,
            target=f"{context.service_name}.{context.method_name}",
            message=SERVICE_DECORATOR_SAFE_ERROR_MESSAGE,
        )

    async def _map_call_args(self, args: list[Any], method_name: str) -> list[Any]:
        next_args = args

        for rule in self._rules:
            if not self._should_apply_rule(rule, method_name) or rule.map_args is None:
                continue

            context = ServiceMapperContext(
                service_name=self._service_name,
                method_name=method_name,
                phase=SERVICE_DECORATOR_PHASE["Encode"],
            )

            try:
                mapped = rule.map_args(next_args, context)
                if inspect.isawaitable(mapped):
                    mapped = await mapped
                next_args = self._ensure_args_array(mapped, context)
            except Exception as error:
                raise self._wrap_transform_error(error, context)

        return next_args

    async def _map_call_result(self, result: Any, method_name: str) -> Any:
        next_result = result

        for rule in self._rules:
            if not self._should_apply_rule(rule, method_name) or rule.map_result is None:
                continue

            context = ServiceMapperContext(
                service_name=self._service_name,
                method_name=method_name,
                phase=SERVICE_DECORATOR_PHASE["Decode"],
            )

            try:
                mapped = rule.map_result(next_result, context)
                if inspect.isawaitable(mapped):
                    mapped = await mapped
                next_result = mapped
            except Exception as error:
                raise self._wrap_transform_error(error, context)

        return next_result
