from meeshkan.nlp.operation_classifier import OperationClassifier


def test_operation_classifier():
    cl = OperationClassifier()
    cl.fill_operations()
