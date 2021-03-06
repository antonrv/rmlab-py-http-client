from aiohttp import FormData
import pytest
from rmlab_http_client.types import (
    AuthType,
    DataRequestContext,
    DataRequestContextMultipart,
    Endpoint,
    FileType,
    MethodType,
    PayloadArguments,
    PayloadType,
    ResponseType,
    DataRequestContext,
)
from rmlab_errors import ValueError


async def resource_vars(*, foo: str, bar: int = 32, zee: float, boo: bool):
    pass


@pytest.mark.parametrize("payload", [PayloadType.MATCH, PayloadType.JSON])
def test_variables(payload: PayloadType):

    pargs = PayloadArguments.make_from_function(resource_vars)

    ep = Endpoint(
        resource=["my", "resource"],
        method=MethodType.POST,
        payload=payload,
        auth=AuthType.PUBLIC,
        response=ResponseType.NONE,
        arguments=pargs,
    )

    rd1 = DataRequestContext.make_data(ep, foo="foovalue", bar=27, zee=12.3, boo=False)

    assert rd1["foo"] == "foovalue"
    assert rd1["bar"] == 27
    assert rd1["zee"] == 12.3
    assert rd1["boo"] == False

    rd2 = DataRequestContext.make_data(ep, foo="foovalue", zee=12.3, boo=True)

    assert rd2["foo"] == "foovalue"
    assert rd2["bar"] == 32
    assert rd2["zee"] == 12.3
    assert rd2["boo"] == True

    with pytest.raises(ValueError):
        # foo missing
        DataRequestContext.make_data(ep, bar=27, zee=12.3, boo=True)

    with pytest.raises(ValueError):
        # foo missing
        DataRequestContext.make_data(ep, zee=12.3, boo=True)

    with pytest.raises(ValueError):
        # zee missing
        DataRequestContext.make_data(ep, foo="foovalue", bar=27, boo=True)

    with pytest.raises(ValueError):
        # zee missing
        DataRequestContext.make_data(ep, foo="foovalue", boo=True)

    with pytest.raises(ValueError):
        # boo missing
        DataRequestContext.make_data(ep, foo="foovalue", zee=12.3)


async def resource_optionals_none(
    *, opt_str: str = None, opt_int: int = None, opt_float: float = None
):
    pass


@pytest.mark.parametrize("payload", [PayloadType.MATCH, PayloadType.JSON])
def test_variables_optionals(payload: PayloadType):

    pargs = PayloadArguments.make_from_function(resource_optionals_none)

    ep = Endpoint(
        resource=["my", "resource"],
        method=MethodType.POST,
        payload=payload,
        auth=AuthType.PUBLIC,
        response=ResponseType.NONE,
        arguments=pargs,
    )

    rd1 = DataRequestContext.make_data(ep, opt_str="foo", opt_int=23, opt_float=14.23)
    assert rd1["opt_str"] == "foo"
    assert rd1["opt_int"] == 23
    assert rd1["opt_float"] == 14.23

    rd2 = DataRequestContext.make_data(ep)
    assert rd2["opt_str"] == None
    assert rd2["opt_int"] == None
    assert rd2["opt_float"] == None


async def resource_containers(
    *, foo_int: int, foo_float: float, bar_dict: dict, bar_list: list
):
    pass


def test_variables_containers_limits():

    with pytest.raises(AssertionError):
        PayloadArguments.make_from_function(
            resource_containers, limits={"not_existing_arg": 1024}
        )

    pargs = PayloadArguments.make_from_function(
        resource_containers,
        limits={"foo_int": 1024, "foo_float": 25.4, "bar_dict": 3, "bar_list": 5},
    )

    ep = Endpoint(
        resource=["my", "resource"],
        method=MethodType.POST,
        payload=PayloadType.JSON,
        auth=AuthType.PUBLIC,
        response=ResponseType.NONE,
        arguments=pargs,
    )

    # ---- All within the limits
    rd1 = DataRequestContext.make_data(
        ep,
        foo_int=1024,
        foo_float=25.4,
        bar_dict={"a": 1, "b": 2, "c": 3},
        bar_list=[1, 2, 3, 4, 5],
    )

    assert rd1["foo_int"] == 1024
    assert rd1["foo_float"] == 25.4
    assert rd1["bar_dict"] == {"a": 1, "b": 2, "c": 3}
    assert rd1["bar_list"] == [1, 2, 3, 4, 5]

    with pytest.raises(ValueError):
        # foo_int exceeds
        DataRequestContext.make_data(
            ep,
            foo_int=1025,
            foo_float=25.4,
            bar_dict={"a": 1, "b": 2, "c": 3},
            bar_list=[1, 2, 3, 4, 5],
        )

    with pytest.raises(ValueError):
        # foo_float exceeds
        DataRequestContext.make_data(
            ep,
            foo_int=1024,
            foo_float=25.5,
            bar_dict={"a": 1, "b": 1, "c": 1},
            bar_list=[1, 2, 3, 4, 5],
        )

    with pytest.raises(ValueError):
        # bar_dict exceeds
        DataRequestContext.make_data(
            ep,
            foo_int=1024,
            foo_float=25.4,
            bar_dict={"a": 1, "b": 2, "c": 3, "d": 1},
            bar_list=[1, 2, 3, 4, 5],
        )

    with pytest.raises(ValueError):
        # bar_list exceeds
        DataRequestContext.make_data(
            ep,
            foo_int=1024,
            foo_float=25.4,
            bar_dict={"a": 1, "b": 2, "c": 3},
            bar_list=[1, 2, 3, 4, 5, 6],
        )


async def resource_file(*, foo: str, bar: int, file_content: FileType):
    pass


def test_files():

    pargs = PayloadArguments.make_from_function(resource_file)

    ep = Endpoint(
        resource=["my", "resource"],
        method=MethodType.POST,
        payload=PayloadType.MULTIPART,
        auth=AuthType.PUBLIC,
        response=ResponseType.NONE,
        arguments=pargs,
    )

    import pathlib

    path = pathlib.Path(__file__).parent.resolve()

    filename = str(path) + "/sample.json"

    with DataRequestContextMultipart(
        ep, foo="foovalue", bar=15, file_content=filename
    ) as data_req:

        assert isinstance(data_req.data, FormData)

    with pytest.raises(ValueError):
        # foo missing
        with DataRequestContextMultipart(ep, bar=15, file_content=filename):
            pass

    with pytest.raises(ValueError):
        # file_content missing
        with DataRequestContextMultipart(ep, foo="foovalue", bar=15):
            pass

    with pytest.raises(FileNotFoundError):
        # file not existing
        with DataRequestContextMultipart(
            ep, foo="foovalue", bar=15, file_content="not_existing"
        ):
            pass
