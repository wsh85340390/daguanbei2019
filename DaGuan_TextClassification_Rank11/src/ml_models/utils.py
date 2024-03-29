import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score
from sklearn.model_selection import cross_val_score, StratifiedKFold
import pandas as pd

from utils.utils import prepare_word_data


def generate_oof_pred(clf, model_name, granularity='word', num_fold=10, seed=2018, silent=False):
    if granularity == 'word':
        train_data, train_label, test_x = prepare_word_data()
    else:
        train_data, train_label, test_x = prepare_word_data()
    num_classes = len(set(train_label))
    fold_len = train_data.shape[0] // num_fold
    skf_indices = []
    skf = StratifiedKFold(n_splits=num_fold, shuffle=True, random_state=seed)
    for i, (train_idx, valid_idx) in enumerate(skf.split(np.ones(train_data.shape[0]), train_label)):
        skf_indices.extend(valid_idx.tolist())
    train_pred = np.zeros((train_data.shape[0], num_classes))
    test_pred = np.zeros((test_x.shape[0], num_classes))
    for fold in range(num_fold):
        if not silent:
            print(f'Processing fold {fold}...')
        fold_start = fold * fold_len
        fold_end = (fold + 1) * fold_len
        if fold == num_fold - 1:
            fold_end = train_data.shape[0]
        train_indices = skf_indices[:fold_start] + skf_indices[fold_end:]
        test_indices = skf_indices[fold_start:fold_end]
        train_x = train_data[train_indices]
        train_y = train_label[train_indices]
        cv_test_x = train_data[test_indices]
        clf.fit(train_x, train_y)
        pred = clf.predict_proba(cv_test_x)
        train_pred[test_indices] = pred
        pred = clf.predict_proba(test_x)
        test_pred += pred / num_fold
    y_pred = np.argmax(train_pred, axis=1)
    score = f1_score(train_label, y_pred, average='macro')
    if not silent:
        np.save(f'../../oof_pred/{model_name}_{granularity}_train_{score:.4f}', train_pred)
        np.save(f'../../oof_pred/{model_name}_{granularity}_test_{score:.4f}', test_pred)
    return score
