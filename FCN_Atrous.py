
# https://github.com/wkentaro/pytorch-fcn/blob/master/torchfcn/models/fcn32s.py
# fc weights into the 1x1 convs  , get_upsampling_weight 



from keras.models import *
from keras.layers import *
import tensorflow as tf
import sys
sys.path.insert(1, './src')
# from crfrnn_layer import CrfRnnLayer
from keras.backend import permute_dimensions
from keras import backend as K


import os
file_path = os.path.dirname( os.path.abspath(__file__) )

VGG_Weights_path = file_path+"/data/vgg16_weights_th_dim_ordering_th_kernels.h5"

IMAGE_ORDERING = 'channels_first' 


def FCN8_Atrous( nClasses ,  input_height=416, input_width=608 , vgg_level=3):

	# assert input_height%32 == 0
	# assert input_width%32 == 0

	# https://github.com/fchollet/deep-learning-models/releases/download/v0.1/vgg16_weights_th_dim_ordering_th_kernels.h5
	img_input = Input(shape=(3,input_height,input_width))
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(img_input)
	x = Conv2D(8, (3, 3), activation='relu', name='block1_conv1', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = Conv2D(8, (3, 3), activation='relu', name='block1_conv2', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(img_input)
	x = MaxPooling2D((3, 3), strides=(2, 2), name='block1_pool', data_format=IMAGE_ORDERING )(x)

	# Block 2
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = Conv2D(16, (3, 3), activation='relu', name='block2_conv1', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = Conv2D(16, (3, 3), activation='relu', name='block2_conv2', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = MaxPooling2D((3, 3), strides=(2, 2), name='block2_pool', data_format=IMAGE_ORDERING )(x)
	f2 = x
	
	# Block 3
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = Conv2D(32, (3, 3), activation='relu', name='block3_conv1', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = Conv2D(32, (3, 3), activation='relu', name='block3_conv2', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = Conv2D(32, (3, 3), activation='relu', name='block3_conv3', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = MaxPooling2D((3, 3), strides=(2, 2), name='block3_pool', data_format=IMAGE_ORDERING )(x)
	f3 = x

	# Block 4
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = Conv2D(64, (3, 3), activation='relu', name='block4_conv1', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = Conv2D(64, (3, 3), activation='relu', name='block4_conv2', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	x = Conv2D(64, (3, 3), activation='relu', name='block4_conv3', data_format=IMAGE_ORDERING )(x)
	x = ZeroPadding2D(padding=(1,1), data_format=IMAGE_ORDERING )(x)
	h = MaxPooling2D((3, 3), strides=(1, 1), name='block4_pool', data_format=IMAGE_ORDERING )(x)
	f4 = x
	
	# Block 5
	h = ZeroPadding2D(padding=(2, 2), data_format=IMAGE_ORDERING)(h)
	h = Conv2D(64, (3, 3),dilation_rate=(2, 2), activation='relu', name='conv5_1', data_format=IMAGE_ORDERING)(h)
	h = ZeroPadding2D(padding=(2, 2), data_format=IMAGE_ORDERING)(h)
	h = Conv2D(64, (3, 3),dilation_rate=(2, 2), activation='relu', name='conv5_2', data_format=IMAGE_ORDERING)(h)
	h = ZeroPadding2D(padding=(2, 2), data_format=IMAGE_ORDERING)(h)
	h = Conv2D(64, (3, 3),dilation_rate=(2, 2), activation='relu', name='conv5_3', data_format=IMAGE_ORDERING)(h)
	h = ZeroPadding2D(padding=(1, 1), data_format=IMAGE_ORDERING)(h)
	p5 = MaxPooling2D(pool_size=(3, 3),strides=(1, 1), data_format=IMAGE_ORDERING)(h)

	# branching for Atrous Spatial Pyramid Pooling
	# hole = 6
	# b1 = ZeroPadding2D(padding=(6, 6))(p5)
	b1 = Conv2D(10, (3, 3), padding='same',dilation_rate=(6, 6), activation='relu', name='fc6_1', data_format=IMAGE_ORDERING)(p5)
	b1 = Dropout(0.5)(b1)
	b1 = Conv2D(10, (1, 1), activation='relu', name='fc7_1', data_format=IMAGE_ORDERING)(b1)
	b1 = Dropout(0.5)(b1)
	b1 = Conv2D(2, (1, 1), activation='relu', name='fc8_voc12_1', data_format=IMAGE_ORDERING)(b1)

	# hole = 12
	# b2 = ZeroPadding2D(padding=(12, 12))(p5)
	b2 = Conv2D(10, (3, 3), padding='same',dilation_rate=(12, 12), activation='relu', name='fc6_2', data_format=IMAGE_ORDERING)(p5)
	b2 = Dropout(0.5)(b2)
	b2 = Conv2D(10, (1, 1), activation='relu', name='fc7_2', data_format=IMAGE_ORDERING)(b2)
	b2 = Dropout(0.5)(b2)
	b2 = Conv2D(2, (1, 1), activation='relu', name='fc8_voc12_2', data_format=IMAGE_ORDERING)(b2)

	# hole = 18
	# b3 = ZeroPadding2D(padding=(18, 18))(p5)
	b3 = Conv2D(10, (3, 3), padding='same',dilation_rate=(18, 18), activation='relu', name='fc6_3', data_format=IMAGE_ORDERING)(p5)
	b3 = Dropout(0.5)(b3)
	b3 = Conv2D(10, (1, 1), activation='relu', name='fc7_3', data_format=IMAGE_ORDERING)(b3)
	b3 = Dropout(0.5)(b3)
	b3 = Conv2D(2, (1, 1), activation='relu', name='fc8_voc12_3', data_format=IMAGE_ORDERING)(b3)

	# hole = 24
	# b4 = ZeroPadding2D(padding=(24, 24))(p5)
	b4 = Conv2D(10, (3, 3), padding='same',dilation_rate=(24, 24), activation='relu', name='fc6_4', data_format=IMAGE_ORDERING)(p5)
	b4 = Dropout(0.5)(b4)
	b4 = Conv2D(10, (1, 1), activation='relu', name='fc7_4', data_format=IMAGE_ORDERING)(b4)
	b4 = Dropout(0.5)(b4)
	b4 = Conv2D(2, (1, 1), activation='relu', name='fc8_voc12_4', data_format=IMAGE_ORDERING)(b4)
	
	
	logits = merge([b1, b2, b3, b4], mode='sum')#remove
	# out = UpSampling2D(size=(8,8), data_format=IMAGE_ORDERING)(logits)
	
	# logits = BilinearUpsampling(upsampling=upsampling)(s)
	
	def mul_minus_one(a):
		return K.resize_images(a,8, 8, data_format=IMAGE_ORDERING)
	def mul_minus_one_output_shape(input_shape):
		return input_shape

	# out = (Activation('softmax'))(logits)
	resize = Lambda(mul_minus_one)
	out = resize(logits)
	# Ensure that the model takes into account
	# any potential predecessors of `input_tensor`.
	inputs = img_input
	
	# Create model.
	# model = Model(inputs, out, name='deeplabV2')
	
	o_shape = Model(img_input ,  out).output_shape
	# print(o_shape)
	# exit(0)
	outputHeight = o_shape[2]
	outputWidth = o_shape[3]
	# print(o_shape)
	
	o = (Reshape((  -1  , outputHeight*outputWidth   )))(out)
	o = (Permute((2, 1)))(o)
	o = (Activation('softmax'))(o)
	model = Model( img_input , o )
	model.outputWidth = outputWidth
	model.outputHeight = outputHeight
	model.summary()
	# exit(0)
	exp_model=model
	return model, exp_model




if __name__ == '__main__':
	m = FCN8( 101 )
	from keras.utils import plot_model
	plot_model( m , show_shapes=True , to_file='model.png')
