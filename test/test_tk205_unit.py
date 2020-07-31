import tk205

'''
Unit tests
'''

def test_objects_near_equal():
    # Numbers
    assert(tk205.util.objects_near_equal(3.0,3.0001,abs_tol=0.01))
    assert(not tk205.util.objects_near_equal(3.0,3.0001,abs_tol=0.0000001))

    # Lists
    assert(tk205.util.objects_near_equal([3.0],[3.0001],abs_tol=0.01))

    # Dictionary
    assert(tk205.util.objects_near_equal({"this":[3.0]},{"this":[3.0001]},abs_tol=0.01))
    assert(not tk205.util.objects_near_equal({"this":[3.0]},{"not_this":[3.0001]},abs_tol=0.01))
