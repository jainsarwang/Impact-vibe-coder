
from flask import Flask, render_template, request, jsonify
import random
import json

app = Flask(__name__)


def bubble_sort(data):
    steps = [list(data)]
    n = len(data)
    for i in range(n):
        for j in range(0, n-i-1):
            if data[j] > data[j+1]:
                data[j], data[j+1] = data[j+1], data[j]
                steps.append(list(data))
    return steps

def insertion_sort(data):
    steps = [list(data)]
    for i in range(1, len(data)):
        key = data[i]
        j = i-1
        while j >= 0 and key < data[j] :
                data[j + 1] = data[j]
                j -= 1
                steps.append(list(data))
        data[j + 1] = key
        steps.append(list(data))
    return steps

def selection_sort(data):
    steps = [list(data)]
    for i in range(len(data)):
        min_idx = i
        for j in range(i+1, len(data)):
            if data[min_idx] > data[j]:
                min_idx = j
        data[i], data[min_idx] = data[min_idx], data[i]
        steps.append(list(data))
    return steps

def merge_sort(data):
    steps = []

    def merge_sort_recursive(data):
        if len(data) > 1:
            mid = len(data) // 2
            left = data[:mid]
            right = data[mid:]

            merge_sort_recursive(left)
            merge_sort_recursive(right)

            i = j = k = 0

            while i < len(left) and j < len(right):
                if left[i] < right[j]:
                    data[k] = left[i]
                    i += 1
                else:
                    data[k] = right[j]
                    j += 1
                k += 1
                steps.append(list(data))

            while i < len(left):
                data[k] = left[i]
                i += 1
                k += 1
                steps.append(list(data))

            while j < len(right):
                data[k] = right[j]
                j += 1
                k += 1
                steps.append(list(data))

    steps.append(list(data))
    merge_sort_recursive(data)
    return steps

def quick_sort(data):
    steps = []

    def quick_sort_recursive(data, low, high):
        if low < high:
            pi = partition(data, low, high)
            quick_sort_recursive(data, low, pi-1)
            quick_sort_recursive(data, pi+1, high)

    def partition(data, low, high):
        i = (low-1)         # index of smaller element
        pivot = data[high]     # pivot

        for j in range(low, high):
            if data[j] <= pivot:
                i += 1
                data[i], data[j] = data[j], data[i]
                steps.append(list(data))

        data[i+1], data[high] = data[high], data[i+1]
        steps.append(list(data))
        return (i+1)

    steps.append(list(data))
    quick_sort_recursive(data, 0, len(data)-1)
    return steps


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/generate_numbers', methods=['POST'])
def generate_numbers():
    num_count = int(request.form['num_count'])
    min_value = int(request.form['min_value'])
    max_value = int(request.form['max_value'])
    numbers = [random.randint(min_value, max_value) for _ in range(num_count)]
    return jsonify(numbers=numbers)

@app.route('/sort', methods=['POST'])
def sort():
    data = json.loads(request.form['data'])
    algorithm = request.form['algorithm']

    if algorithm == 'bubble':
        steps = bubble_sort(data)
    elif algorithm == 'insertion':
        steps = insertion_sort(data)
    elif algorithm == 'selection':
        steps = selection_sort(data)
    elif algorithm == 'merge':
        steps = merge_sort(data)
    elif algorithm == 'quick':
        steps = quick_sort(data)
    else:
        return jsonify(error='Invalid algorithm'), 400

    return jsonify(steps=steps)

if __name__ == '__main__':
    app.run(debug=True)
