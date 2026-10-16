import importlib.util
import unittest
from pathlib import Path

source = Path(__file__).resolve().parents[1] / "scripts" / "configure_genesis.py"
spec = importlib.util.spec_from_file_location("bajar_genesis", source)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

class GenesisTests(unittest.TestCase):
    def original(self):
        return {
            "config": {"chainId": 1337, "qbft": {"blockperiodseconds": 5, "blockreward": "99"}},
            "extraData": "0xQBFT_SAMPLE",
            "alloc": {
                "0x1111111111111111111111111111111111111111": {
                    "balance": "9999", "privateKey": "SHOULD_NOT_SURVIVE"},
                "0x2222222222222222222222222222222222222": {
                    "balance": "2", "code": "0x6000", "storage": {}}
            }
        }

    def test_genesis_supply_and_privacy(self):
        result = module.configure(self.original())
        self.assertEqual(result["config"]["chainId"], 131313)
        self.assertNotIn("blockreward", result["config"]["qbft"])
        self.assertEqual(result["alloc"][module.DEV_FAUCET]["balance"], str(3_000_000_000 * 10**18))
        self.assertEqual(result["alloc"][module.DEV_RESERVE]["balance"], str(10_000_000_000 * 10**18))
        self.assertEqual(len(result["alloc"]), 3)
        self.assertEqual(result["alloc"]["0x2222222222222222222222222222222222222222"]["code"], "0x6000")
        self.assertNotIn("privateKey", str(result))

    def test_reject_wrong_network(self):
        original = self.original()
        original["config"]["chainId"] = 1
        with self.assertRaises(ValueError):
            module.configure(original)

    def test_reject_non_qbft(self):
        original = self.original()
        del original["config"]["qbft"]
        with self.assertRaises(ValueError):
            module.configure(original)

if __name__ == "__main__":
    unittest.main()

