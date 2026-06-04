import unittest

from dusk_api.contracts import ServiceDecoratorConfig, ServiceDecoratorRule
from dusk_api.modules.service import SERVICE_DECORATOR_PHASE, ServiceDecorator, ServiceDecoratorTransformError


class _Service:
    async def save(self, input_data: dict[str, str]):
        return {"ok": True, "payload": input_data}


class TestService(unittest.IsolatedAsyncioTestCase):
    async def test_domain__method_rule__maps_args_and_result_for_target_method(self) -> None:
        service = _Service()

        async def map_args(args, _context):
            first = args[0]
            return [{**first, "secret": f"enc:{first['secret']}"}]

        async def map_result(result, _context):
            payload = result["payload"]
            return {**result, "payload": {**payload, "secret": payload["secret"].replace("enc:", "")}}

        decorated = ServiceDecorator(
            service,
            ServiceDecoratorConfig(
                service_name="vault",
                rules=[ServiceDecoratorRule(methods=["save"], map_args=map_args, map_result=map_result)],
            ),
        ).decorate()

        saved = await decorated.save({"secret": "abc", "keep": "x"})
        self.assertEqual(saved, {"ok": True, "payload": {"secret": "abc", "keep": "x"}})

    async def test_complement__invalid_args_mapper_output__throws_typed_error(self) -> None:
        service = _Service()

        async def invalid_args(_args, _context):
            return {"invalid": True}

        decorated = ServiceDecorator(
            service,
            ServiceDecoratorConfig(service_name="vault", rules=[ServiceDecoratorRule(map_args=invalid_args)]),
        ).decorate()

        with self.assertRaises(ServiceDecoratorTransformError) as error:
            await decorated.save({"secret": "abc"})

        self.assertEqual(error.exception.code, "SERVICE_DECORATOR_TRANSFORM_ERROR")
        self.assertEqual(error.exception.phase, SERVICE_DECORATOR_PHASE["Encode"])
