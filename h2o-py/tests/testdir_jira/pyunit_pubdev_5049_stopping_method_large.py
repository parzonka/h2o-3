from __future__ import print_function
import sys

sys.path.insert(1, "../../")
import h2o
from tests import pyunit_utils
from h2o.estimators.deeplearning import H2ODeepLearningEstimator
from h2o.exceptions import H2OResponseError

'''
    This function will test if the stopping_method has been implemented correctly for the model type what was
    sent.  In particular, it will perform the following tests:
    1. Check to make sure stopping_method is checked and errors be thrown when
        a. setting it to valid when a validation set if not provided;
        b. setting it to xval when no cross validation is enabled;
    2. when stopping_method is set to xval, the scoring history should be the same as if not stopping_method is
    chosen by cross-validation was enabled.  Compare the two and make sure they are the same
    3. when the stopping_method is set to valid, the scoring history should be the same as if not stopping_method is
    chosen, cross-validation is disabled, a validation is provided.  Compare the two and make sure they are the same
    4. when the stopping_method is set to train, the scoring history should be the same as if not stopping_method is
    chosen, no validation is provided.  Compare the two and make sure they are the same
'''


def test_stopping_method():
    # deeplearning\
    seed = 12345
    training1_data = h2o.import_file(path=pyunit_utils.locate("smalldata/gridsearch/gaussian_training1_set.csv"))
    validation_data = h2o.import_file(path=pyunit_utils.locate("smalldata/gridsearch/gaussian_training2_set.csv"))
    y_index = training1_data.ncol - 1
    x_indices = list(range(y_index))
    testStoppingMethod(0, training1_data, x_indices, y_index, validation_data, seed)


def testStoppingMethod(model_index, training_data, x_indices, y_index, validation_data, seed):
    '''
    This function will test if the stopping_method has been implemented correctly for the model type what was
    sent.  In particular, it will perform the following tests:
    1. Check to make sure stopping_method is checked and errors be thrown when
        a. setting it to valid when a validation set if not provided;
        b. setting it to xval when no cross validation is enabled;
    2. when stopping_method is set to xval, the scoring history should be the same as if not stopping_method is
    chosen by cross-validation was enabled.  Compare the two and make sure they are the same
    3. when the stopping_method is set to valid, the scoring history should be the same as if not stopping_method is
    chosen, cross-validation is disabled, a validation is provided.  Compare the two and make sure they are the same
    4. when the stopping_method is set to train, the scoring history should be the same as if not stopping_method is
    chosen, no validation is provided.  Compare the two and make sure they are the same

    :param model_index: choose model to be tested, 0 for deeplearning, 1 for GBM or 2 for RF
    :param training_data: training data frame
    :param x_indices: predictor column lists
    :param y_index: response column
    :param validation_data: validation dataset
    :return: pass or fail the test
    '''
    models_sm_valid_bad = ["H2ODeepLearningEstimator(distribution='gaussian', seed=seed, hidden=[3], "
                           "stopping_method='valid', stopping_rounds=3, stopping_tolerance=0.01, nfolds=3)"]
    models_sm_xval_bad = ["H2ODeepLearningEstimator(distribution='gaussian', seed=seed, hidden=[3], "
                          "stopping_method='xval', stopping_rounds=3, stopping_tolerance=0.01)"]

    models_sm_xval = [
        "H2ODeepLearningEstimator(distribution='gaussian', seed=seed, hidden=[3], stopping_method='xval', stopping_rounds=3, stopping_tolerance=0.01, nfolds=3)"]
    models_sm_valid = [
        "H2ODeepLearningEstimator(distribution='gaussian', seed=seed, hidden=[3], stopping_method='valid', stopping_rounds=3, stopping_tolerance=0.01, nfolds=3)"]
    models_sm_train = [
        "H2ODeepLearningEstimator(distribution='gaussian', seed=seed, hidden=[3], stopping_method='train', stopping_rounds=3, stopping_tolerance=0.01, nfolds=3)"]

    models_auto_CV = [
        "H2ODeepLearningEstimator(distribution='gaussian', seed=123456, hidden=[3], stopping_rounds=3, stopping_tolerance=0.01, nfolds=3)"]
    models_auto_noCV = [
        "H2ODeepLearningEstimator(distribution='gaussian', seed=123456, hidden=[3], stopping_rounds=3, stopping_tolerance=0.01)"]

    # test 1, set stopping method to valid without a validation set
    try:
        model = eval(models_sm_valid_bad[model_index])
        model.train(x=x_indices, y=y_index, training_frame=training_data)
    except H2OResponseError:
        print("Exception expected and thrown: setting stopping method to valid without a validation frame.")

    # test 2, set stopping method to xval without enabling cross-validation
    try:
        model = eval(models_sm_xval_bad[model_index])
        model.train(x=x_indices, y=y_index, training_frame=training_data, validation_frame=validation_data)
    except H2OResponseError:
        print("Exception expected and thrown: setting stopping method to xval without enabling cross-validation.")

    # test 3, compare scoring history of auto with cross-validation and stopping method to xval
    col_header_list = ["training_rmse", "training_deviance", "training_mae", "training_r2"]
    model_auto = eval(models_auto_CV[model_index])
    model_auto.train(x=x_indices, y=y_index, training_frame=training_data)

    model = eval(models_sm_xval[model_index])
    model.train(x=x_indices, y=y_index, training_frame=training_data, validation_frame=validation_data)
    pyunit_utils.assert_H2OTwoDimTable_equal(model_auto._model_json["output"]["scoring_history"],
                                             model._model_json["output"]["scoring_history"], col_header_list,
                                             tolerance=1e-6, check_sign=True, check_all=True,
                                  num_per_dim=100)
    # test 4, compare scoring history of auto without cross-valiation but with validation dataset and stopping method set to valid
    # test 5, compare scoring history of auto without cross-validation and validation datset, stopping method set to train

    if __name__ == "__main__":
        pyunit_utils.standalone_test(test_stopping_method)
    else:
        test_stopping_method()
