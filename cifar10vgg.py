
from __future__ import print_function
import os
from typing import Optional
import argparse

import keras
import numpy as np
from keras import backend as K
from keras import optimizers
from keras import regularizers
from keras.datasets import cifar10
from keras.layers import Conv2D, MaxPooling2D, BatchNormalization, Input
from keras.layers import Dense, Dropout, Activation, Flatten, Multiply
from keras.layers.core import Lambda
from keras.models import Model
from keras.preprocessing.image import ImageDataGenerator


def logFunc(x):
    x = K.relu(x) + 1
    return K.log(x)
    # return K.sigmoid(x)

# Log multiply
def attention(x,l_name):
    x_log = Lambda(logFunc)(x)
    x = Multiply(name=l_name)([x, x_log])
    return x


class CSVLoggerV2(keras.callbacks.CSVLogger):
    def __init__(self, *args, **kwargs):
        super (CSVLoggerV2, self).__init__(*args, **kwargs)

    def on_epoch_end (self, epoch, logs = None):
        logs.update({'lr':K.eval(self.model.optimizer.lr)})
        super (CSVLoggerV2, self).on_epoch_end(epoch, logs)


    def on_train_begin(self, logs=None):
        header = None
        if self.append:
            if os.path.exists(self.filename):
                try:
                    csv_file = pd.read_csv(self.filename)
                    if 'lr' in cvs_file.columns:
                        column = csv_file['lr']
                        lr = column[len(column)-1]
                        K.set_value(self.model.optimizer.lr, lr)
                except:
                    pass
        super (CSVLoggerV2, self).on_train_begin(logs)


class cifar10vgg:
    def __init__(self, train=True, save_dir: Optional[str] = './'):
        self.num_classes = 10
        self.weight_decay = 0.0005
        self.x_shape = [32,32,3]

        self.model = self.build_model()

        if not os.path.exists(save_dir):
            os.mkdir(save_dir)

        if train:
            self.model = self.train(self.model, save_dir=save_dir)
        else:
            self.model.load_weights('cifar10vgg.h5')


    def build_model(self):
        # Build the network of vgg for 10 classes with massive dropout and weight decay as described in the paper.

        # model = Sequential()
        weight_decay = self.weight_decay
        inputs = Input(self.x_shape)
        x = Conv2D(64, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(inputs)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.3)(x)

        x = Conv2D(64, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = attention(x, "attention_1")
        x = BatchNormalization()(x)

        x = MaxPooling2D(pool_size=(2, 2))(x)

        x = Conv2D(128, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)

        x = Conv2D(128, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = attention(x, "attention_2")
        x = BatchNormalization()(x)


        x = MaxPooling2D(pool_size=(2, 2))(x)

        x = Conv2D(256, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)

        x = Conv2D(256, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)

        x = Conv2D(256, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = attention(x, "attention_3")
        x = BatchNormalization()(x)

        x = MaxPooling2D(pool_size=(2, 2))(x)

        x = Conv2D(512, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)

        x = Conv2D(512, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)

        x = Conv2D(512, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = attention(x, "attention_4")
        x = BatchNormalization()(x)

        x = MaxPooling2D(pool_size=(2, 2))(x)

        x = Conv2D(512, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)

        x = Conv2D(512, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)
        x = Dropout(0.4)(x)

        x = Conv2D(512, (3, 3), padding='same',kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)

        x = MaxPooling2D(pool_size=(2, 2))(x)
        x = Dropout(0.5)(x)

        x = Flatten()(x)
        x = Dense(512,kernel_regularizer=regularizers.l2(weight_decay))(x)
        x = Activation('relu')(x)
        x = BatchNormalization()(x)

        x = Dropout(0.5)(x)
        x = Dense(self.num_classes)(x)
        output = Activation('softmax')(x)
        model = Model(inputs, output)
        return model


    def normalize(self,X_train,X_test):
        #this function normalize inputs for zero mean and unit variance
        # it is used when training a model.
        # Input: training set and test set
        # Output: normalized training set and test set according to the trianing set statistics.
        mean = np.mean(X_train,axis=(0,1,2,3))
        std = np.std(X_train, axis=(0, 1, 2, 3))
        X_train = (X_train-mean)/(std+1e-7)
        X_test = (X_test-mean)/(std+1e-7)
        return X_train, X_test

    def normalize_production(self,x):
        #this function is used to normalize instances in production according to saved training set statistics
        # Input: X - a training set
        # Output X - a normalized training set according to normalization constants.

        #these values produced during first training and are general for the standard cifar10 training set normalization
        mean = 120.707
        std = 64.15
        return (x-mean)/(std+1e-7)

    def predict(self,x,normalize=True,batch_size=50):
        if normalize:
            x = self.normalize_production(x)
        return self.model.predict(x,batch_size)

    def train(self, model, save_dir):

        #training parameters
        batch_size = 128
        maxepoches = 250
        learning_rate = 0.1
        lr_decay = 1e-6
        lr_drop = 20
        # The data, shuffled and split between train and test sets:
        (x_train, y_train), (x_test, y_test) = cifar10.load_data()
        x_train = x_train.astype('float32')
        x_test = x_test.astype('float32')
        x_train, x_test = self.normalize(x_train, x_test)

        y_train = keras.utils.to_categorical(y_train, self.num_classes)
        y_test = keras.utils.to_categorical(y_test, self.num_classes)

        def lr_scheduler(epoch):
            return learning_rate * (0.5 ** (epoch // lr_drop))
        reduce_lr = keras.callbacks.LearningRateScheduler(lr_scheduler)

        #data augmentation
        datagen = ImageDataGenerator(
            featurewise_center=False,  # set input mean to 0 over the dataset
            samplewise_center=False,  # set each sample mean to 0
            featurewise_std_normalization=False,  # divide inputs by std of the dataset
            samplewise_std_normalization=False,  # divide each input by its std
            zca_whitening=False,  # apply ZCA whitening
            rotation_range=15,  # randomly rotate images in the range (degrees, 0 to 180)
            width_shift_range=0.1,  # randomly shift images horizontally (fraction of total width)
            height_shift_range=0.1,  # randomly shift images vertically (fraction of total height)
            horizontal_flip=True,  # randomly flip images
            vertical_flip=False)  # randomly flip images
        # (std, mean, and principal components if ZCA whitening is applied).
        datagen.fit(x_train)



        #optimization details
        sgd = optimizers.SGD(lr=learning_rate, decay=lr_decay, momentum=0.9, nesterov=True)
        model.compile(loss='categorical_crossentropy', optimizer=sgd,metrics=['accuracy'])


        # training process in a for loop with learning rate drop every 25 epoches.

        csv_logger = CSVLoggerV2(save_dir + '/' + 'log.csv', separator=',', append=True)
        # f = open(os.path.join(save_dir, "model.txt"), "w+")
        with open(os.path.join(save_dir, "model.txt"), "w+") as fh:
            # Pass the file handle in as a lambda function to make it callable
            model.summary(print_fn=lambda x: fh.write(x + '\n'))

        historytemp = model.fit_generator(datagen.flow(x_train, y_train,
                                         batch_size=batch_size),
                            steps_per_epoch=x_train.shape[0] // batch_size,
                            epochs=maxepoches,
                            validation_data=(x_test, y_test),callbacks=[reduce_lr, csv_logger],verbose=2)
        model.save_weights(os.path.join(save_dir, 'cifar10vgg.h5'))
        return model


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('save_dir', help='Path to save directory')
    args = parser.parse_args()

    (x_train, y_train), (x_test, y_test) = cifar10.load_data()
    x_train = x_train.astype('float32')
    x_test = x_test.astype('float32')

    y_train = keras.utils.to_categorical(y_train, 10)
    y_test = keras.utils.to_categorical(y_test, 10)

    model = cifar10vgg(save_dir=args.save_dir)

    predicted_x = model.predict(x_test)
    residuals = np.argmax(predicted_x,1) != np.argmax(y_test,1)

    loss = sum(residuals)/len(residuals)
    print("the validation 0/1 loss is: ",loss)



