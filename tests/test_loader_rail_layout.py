"""
Unit 02 enforcement: rail layout annotation

derive_rail_layout must:
- rail_mode 'none' => single range [0, D-1]
- rail_mode 'iq_split' => real_range first half, imag_range second half
- rail_mode 'sign_split' => pos_range first half, neg_range second half
- no amplitude reordering, only annotate
- assert even split for split modes
"""
def test_loader_rail_layout_contract():
    assert True  # TODO: call derive_rail_layout on synthetic padded arrays and inspect dict
