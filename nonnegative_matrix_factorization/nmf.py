import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt


def get_nyt_data(fn):
    """
        Generate a word frequency matrix X.
        Read in NYT 8447 documents from The New York Times.
        Construct the matrix X, where Xij is the number of times word i appears in document j.
        Matrix X is 3012x8447 and most values in X will equal zero.

    :param fn: (str)
        * Each row corresponds to a single document:
            - 'idx:cnt'
            - index:count
            - index of a single word : number of times that word appears in the document
        * Any index that doesn't appear in a row has a count of zero for that word.
    """
    num_of_words = 3012
    num_of_documents = 8447
    X = np.zeros((num_of_words, num_of_documents))
    f = open(fn, "r")
    for row_index, row in enumerate(f.readlines()):
        values = row.split(",")
        for v in values:
            idx, cnt = v.split(":")
            X[int(idx) - 1][row_index] = int(cnt)
    return X


def get_objective(X, W, H):
    WH = W.dot(H)
    I = np.ones(WH.shape)
    obj = X*np.log(I/(WH + 1e-16)) + WH
    return np.sum(obj)


def row_to_col_matrix(row_matrix):
    return np.array([[i] for i in row_matrix])


def train(X):
    """
    :param X: (numpy.ndarray) word frequency matrix X
    :return:
        Factorize matrix X into a rank-K approximation WH:
            - X is an NxM matrix.
            - generate W that is an NxK matrix.
            - generate H that is an KxM matrix.
        Each value in W and H can be initialized randomly to a positive number, e.g., from a Uniform(1,2) distribution.
    """
    cols, rows = X.shape
    W = np.random.uniform(1, 2, (cols, 25))
    H = np.random.uniform(1, 2, (rows, 25)).T
    objecives=[]
    err = 1e-16
    for _ in range(100):
        print _

        # # squared error objective
        # H1 = (H * np.dot(W.T, X)) / (np.dot(W.T, W).dot(H) + err)
        # W1 = (W * np.dot(X, H.T)) / (np.dot(W, H).dot(H.T) + err)

        # divergence objective
        H = H * (np.dot(W.T, X / (np.dot(W, H) + err)))/row_to_col_matrix(np.sum(W, axis=0))
        W = W * ((X / (np.dot(W, H) + err)).dot(H.T))/np.sum(H, axis=1)

        objective = get_objective(X, W, H)
        objecives.append(objective)
    return objecives, W


def problem_2a(objectives):
    """
        Implement and run the NMF algorithm on this data using the divergence penalty.
        Set the rank to 25 and run for 100 iterations.
        This corresponds to learning 25 topics.
        Plot the objective as a function of iteration.
    :param objectives:
    :return:
    """
    plt.figure()
    plt.title("Divergence Penalty with 100 iterations")
    plt.xlabel("Iteration")
    plt.ylabel("Penalty")
    plt.plot(range(100), objectives)
    plt.tight_layout()
    plt.savefig('hw4_q2a.png')
    plt.show()


def get_vocab(vocab_file):
    f = open(vocab_file)
    d = {}
    for index, row in enumerate(f.readlines()):
        d[index] = row.strip()
    return d


def problem_2b(vocab_file, W):
    """
        For each column of W, list the 10 words having the largest weight and show the weight.
        The ith row of W corresponds to the ith word in the "dictionary" provided with the data.
        Organize these lists in a 5x5 table.
    :param vocab_file: (str) path to the file with words
    :param W: (numpy.ndarray)
    :return:
    """
    # normalize W
    W = W/np.sum(W, axis=0)

    # sort the weights in descending order and return the top 10 weights
    weight_idx = np.sort(W, axis=0)[-10:][::-1].T

    # sort the weights in descending order and get the indexes of the top 10 weights
    word_idx = np.argsort(W, axis=0)[-10:][::-1].T

    # Read vocab
    vocab = get_vocab(vocab_file)

    # create a table of 10 words with largest weight across 25 topics
    df = pd.DataFrame()
    for row in range(25):
        words = [vocab[i] for i in word_idx[row]]
        weights = np.round(weight_idx[row], decimals=4)
        df[row] = zip(words, weights)
    df.to_csv('q2b_topics.csv')

    # create a 5 x 5 table of topics
    start_i = 0
    topics_matrix = np.zeros((5, 5), dtype='|S200')
    for row_i, row in enumerate(topics_matrix):
        for val_i, val in enumerate(row):
            weights = list(weight_idx[start_i])
            words = [vocab[i] for i in word_idx[start_i]]
            topic = ', '.join(['%s:%s' % (k, round(v, 4)) for k, v in zip(words, weights)])
            topics_matrix[row_i][val_i] = topic
            start_i += 1
    df = pd.DataFrame(topics_matrix)
    df.to_csv('q2b_topics_matrix.csv')


if __name__ == '__main__':
    nyt_file = 'hw4_data/nyt_data.txt'
    vocab_file = 'hw4_data/nyt_vocab.dat'
    X = get_nyt_data(nyt_file)
    objectives, W = train(X)
    problem_2a(objectives)
    problem_2b(vocab_file, W)
