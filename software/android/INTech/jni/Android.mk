LOCAL_PATH := $(call my-dir)

include $(CLEAR_VARS)

include C:\Android\opencv\native\jni\OpenCV.mk

LOCAL_MODULE    := native_analyze
LOCAL_SRC_FILES := java.cpp ball.cpp ballidentifier.cpp model.cpp morpho.cpp processing.cpp
LOCAL_LDLIBS +=  -llog -ldl
LOCAL_CFLAGS    := -DCOMPILE_FOR_ANDROID

include $(BUILD_SHARED_LIBRARY)
