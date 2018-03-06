import os
os.environ["THEANO_FLAGS"] = "mode=FAST_RUN,device=gpu,floatX=float32"
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ["CUDA_VISIBLE_DEVICES"]="2,1,0"

from sklearn.metrics import accuracy_score
import numpy as np
import matplotlib.pyplot as plt
import gc
from sklearn.metrics import confusion_matrix
import Plot
from pylab import *
import collections
from sklearn.metrics import precision_recall_fscore_support
import BuildModel
import pylab
from keras.callbacks import ModelCheckpoint
np.random.seed(7)


def Text_classification(X_train, X_train_M, y_train, X_test, X_test_M, y_test,
                        Random_Deep,n_epochs,batch_size,sparse_categorical,
                        EMBEDDING_DIM,MAX_SEQUENCE_LENGTH,
                         word_index, embeddings_index):

    y_proba = []
    History = []
    score = []
    number_of_classes = np.max(y_train)+1
    i = 0
    while i < Random_Deep[0]:
        # model_DNN.append(Sequential())
        try:
            print("DNN " + str(i))
            filepath = "weights\weights_DNN_" + str(i) + ".hdf5"
            checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True,
                                         mode='max')
            callbacks_list = [checkpoint]

            model_DNN, model_tmp = BuildModel.buildModel_DNN_Tex(X_train.shape[1], number_of_classes,
                                                                 sparse_categorical)
            h = model_DNN.fit(X_train, y_train,
                              validation_data=(X_test, y_test),
                              epochs=n_epochs[0],
                              batch_size=batch_size,
                              callbacks=callbacks_list,
                              verbose=2)
            History.append(h)

            model_tmp.load_weights(filepath)
            if sparse_categorical == 0:
                model_tmp.compile(loss='sparse_categorical_crossentropy',
                                  optimizer='adam',
                                  metrics=['accuracy'])

                y_pr = model_tmp.predict_classes(X_test, batch_size=batch_size)
                y_proba.append(np.array(y_pr))
                score.append(accuracy_score(y_test, y_pr))
            else:
                model_tmp.compile(loss='categorical_crossentropy',
                                  optimizer='adam',
                                  metrics=['accuracy'])
                y_pr = model_tmp.predict(X_test, batch_size=batch_size)
                y_pr = np.argmax(y_pr, axis=1)
                y_proba.append(np.array(y_pr))
                y_test_temp = np.argmax(y_test, axis=1)
                score.append(accuracy_score(y_test_temp, y_pr))
            # print(y_proba)
            i += 1
            del model_tmp
            del model_DNN
        except:
            print("Error in model ", i, "   try to re-generate an other model")
    del X_train
    del X_test
    gc.collect()

    # for i in range(0, Random_Deep[1]):
    #   model_CNN.append(Sequential())
    i = 0
    while i < Random_Deep[1]:
        try:
            print("CNN" + str(i))

            model_CNN, model_tmp = BuildModel.buildModel_CNN(word_index, embeddings_index, number_of_classes,
                                                             MAX_SEQUENCE_LENGTH, EMBEDDING_DIM, 1, sparse_categorical)

            filepath = "weights\weights_CNN_" + str(i) + ".hdf5"
            checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True,
                                         mode='max')
            callbacks_list = [checkpoint]

            h = model_CNN.fit(X_train_M, y_train,
                              validation_data=(X_test_M, y_test),
                              epochs=n_epochs[1],
                              batch_size=batch_size,
                              callbacks=callbacks_list,
                              verbose=2)
            History.append(h)
            model_tmp.load_weights(filepath)
            if sparse_categorical == 0:
                model_tmp.compile(loss='sparse_categorical_crossentropy',
                                  optimizer='rmsprop',
                                  metrics=['accuracy'])
            else:
                model_tmp.compile(loss='categorical_crossentropy',
                                  optimizer='rmsprop',
                                  metrics=['accuracy'])
            y_pr = model_tmp.predict(X_test_M, batch_size=batch_size)
            y_pr = np.argmax(y_pr, axis=1)
            y_proba.append(np.array(y_pr))

            if sparse_categorical == 0:
                score.append(accuracy_score(y_test, y_pr))
            else:
                y_test_temp = np.argmax(y_test, axis=1)
                score.append(accuracy_score(y_test_temp, y_pr))
            i += 1

            del model_tmp
            del model_CNN
            gc.collect()
        except:
            print("Error in model ", i, "   try to re-generate an other model")

    gc.collect()
    while i < Random_Deep[2]:
        try:
            print("RNN " + str(i))
            filepath = "weights\weights_RNN_" + str(i) + ".hdf5"
            checkpoint = ModelCheckpoint(filepath, monitor='val_acc', verbose=1, save_best_only=True,
                                         mode='max')
            callbacks_list = [checkpoint]

            model_RNN, model_tmp = BuildModel.buildModel_RNN(word_index, embeddings_index, number_of_classes,
                                                                MAX_SEQUENCE_LENGTH, EMBEDDING_DIM, sparse_categorical)

            h = model_RNN.fit(X_train_M, y_train,
                                 validation_data=(X_test_M, y_test),
                                 epochs=n_epochs[2],
                                 batch_size=batch_size,
                                 callbacks=callbacks_list,
                                 verbose=2)
            History.append(h)

            if sparse_categorical == 0:
                model_tmp.load_weights(filepath)
                model_tmp.compile(loss='sparse_categorical_crossentropy',
                                  optimizer='rmsprop',
                                  metrics=['accuracy'])
                y_pr = model_tmp.predict_classes(X_test_M, batch_size=batch_size)
                y_proba.append(np.array(y_pr))
                score.append(accuracy_score(y_test, y_pr))
            else:
                model_tmp.load_weights(filepath)
                model_tmp.compile(loss='categorical_crossentropy',
                                  optimizer='rmsprop',
                                  metrics=['accuracy'])
                y_pr = model_tmp.predict(X_test_M, batch_size=batch_size)
                y_pr = np.argmax(y_pr, axis=1)
                y_proba.append(np.array(y_pr))
                y_test_temp = np.argmax(y_test, axis=1)
                score.append(accuracy_score(y_test_temp, y_pr))
            i += 1
            del model_tmp
            gc.collect()
        except:
            print("Error in model ", i, "   try to re-generate an other model")
        del model_RNN
    gc.collect()
    # Plot.plot_RMDL(History)# plot histori of all RDL models
    y_proba = np.array(y_proba).transpose()

    final_y = []
    for i in range(0, y_proba.shape[0]):
        a = np.array(y_proba[i, :])
        a = collections.Counter(a).most_common()[0][0]
        final_y.append(a)
    if sparse_categorical == 0:
        F_score = accuracy_score(y_test, final_y)
        F1 = precision_recall_fscore_support(y_test, final_y, average='micro')
        F2 = precision_recall_fscore_support(y_test, final_y, average='macro')
        F3 = precision_recall_fscore_support(y_test, final_y, average='weighted')
        cnf_matrix = confusion_matrix(y_test, final_y)
        # Compute confusion matrix
        # Plot non-normalized confusion matrix

        plt.plot(range(10))
        plt.figure()
        classes = list(range(0, np.max(y_test)))
        Plot.plot_confusion_matrix(cnf_matrix, classes=classes,
                                   title='Confusion matrix, without normalization')

        # Plot normalized confusion matrix
        plt.figure()
        Plot.plot_confusion_matrix(cnf_matrix, classes=classes, normalize=True,
                                   title='Normalized confusion matrix')
    else:
        y_test_temp = np.argmax(y_test, axis=1)
        F_score = accuracy_score(y_test_temp, final_y)
        F1 = precision_recall_fscore_support(y_test_temp, final_y, average='micro')
        F2 = precision_recall_fscore_support(y_test_temp, final_y, average='macro')
        F3 = precision_recall_fscore_support(y_test_temp, final_y, average='weighted')
    print(y_proba.shape)
    print(score)
    print(F_score)
    print(F1)
    print(F2)
    print(F3)