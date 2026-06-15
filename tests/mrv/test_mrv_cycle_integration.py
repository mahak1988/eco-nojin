import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from api.services.iot.iot_data_simulator import IoTDataSimulator
from api.services.mrv.mrv_calculator import MRVCalculator
from api.services.carbon.carbon_credit_issuer import CarbonCreditIssuer
from api.services.pes.pes_payment_system import PESPaymentSystem

def test_full_cycle():
    sim, calc, iss, pes = IoTDataSimulator(), MRVCalculator(), CarbonCreditIssuer(), PESPaymentSystem()
    data = sim.simulate_sensor_readings("dishmok", 90)
    mrv = calc.generate_mrv_report(data)
    cr = iss.issue_credits(mrv)
    pay = pes.calculate_payments(mrv, cr)
    assert mrv["carbon"]["total_sequestration_tCO2"] > 0
    assert cr["blockchain_tx_hash"].startswith("0x")
    assert pay["total_payment_usd"] > 0
    print("✅ تست چرخه کامل با موفقیت گذشت")

if __name__ == "__main__": test_full_cycle()