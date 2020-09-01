from ofx_processor.utils.base_ofx import OfxBaseLine
from tests.utils import OfxTransaction


def test_name():
    name = "VIR INST"
    transaction = OfxTransaction(name=name)

    result_name = OfxBaseLine(transaction).get_payee()
    assert result_name == name
