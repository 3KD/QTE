from physics.lorentz import boost_x, preserves_minkowski

def test_boost_preserves_minkowski_metric():
    for beta in [ -0.8, -0.2, 0.0, 0.2, 0.8 ]:
        L = boost_x(beta)
        assert preserves_minkowski(L)

def test_two_boosts_compose_and_preserve():
    L1 = boost_x(0.6)
    L2 = boost_x(-0.3)
    L = L2 @ L1
    assert preserves_minkowski(L)
