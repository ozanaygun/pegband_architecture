# Makefile for a C++ program

# Compiler and flags
CXX = g++
CXXFLAGS = -std=c++20 -Wall -O3 -DLOCAL -pthread

# Source files and target executable
SRC = client.cpp
TARGET = client

# Build target
all: $(TARGET)

$(TARGET): $(SRC)
	$(CXX) $(CXXFLAGS) -o $(TARGET) $(SRC)

# Clean build files
clean:
	rm -f $(TARGET)
