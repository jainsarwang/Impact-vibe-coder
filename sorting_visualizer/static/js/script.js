document.addEventListener('DOMContentLoaded', function() {
    const numCountInput = document.getElementById('num_count');
    const minValueInput = document.getElementById('min_value');
    const maxValueInput = document.getElementById('max_value');
    const generateNumbersButton = document.getElementById('generate_numbers');
    const algorithmSelect = document.getElementById('algorithm');
    const sortButton = document.getElementById('sort');
    const sortingChartCanvas = document.getElementById('sortingChart').getContext('2d');
    const stepsList = document.getElementById('steps-list');

    let sortingChart = null;
    let numbers = [];
    let steps = [];
    let stepIndex = 0;

    generateNumbersButton.addEventListener('click', function() {
        const numCount = parseInt(numCountInput.value);
        const minValue = parseInt(minValueInput.value);
        const maxValue = parseInt(maxValueInput.value);

        fetch('/generate_numbers', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `num_count=${numCount}&min_value=${minValue}&max_value=${maxValue}`
        })
        .then(response => response.json())
        .then(data => {
            numbers = data.numbers;
            updateChart(numbers);
            stepsList.innerHTML = '';
            steps = [];
            stepIndex = 0;
        });
    });

    sortButton.addEventListener('click', function() {
        const algorithm = algorithmSelect.value;

        fetch('/sort', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/x-www-form-urlencoded',
            },
            body: `algorithm=${algorithm}&data=${JSON.stringify(numbers)}`
        })
        .then(response => response.json())
        .then(data => {
            steps = data.steps;
            stepIndex = 0;
            updateChart(steps[0]);
            displaySteps();
        });
    });

    function updateChart(data) {
        if (sortingChart) {
            sortingChart.destroy();
        }

        sortingChart = new Chart(sortingChartCanvas, {
            type: 'bar',
            data: {
                labels: data.map((_, i) => i),
                datasets: [{
                    label: 'Numbers',
                    data: data,
                    backgroundColor: 'rgba(0, 119, 255, 0.8)',
                    borderColor: 'rgba(0, 119, 255, 1)',
                    borderWidth: 1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true
                    }
                }
            }
        });
    }

    function displaySteps() {
        stepsList.innerHTML = '';
        steps.forEach((step, index) => {
            const listItem = document.createElement('li');
            listItem.textContent = `Step ${index + 1}: [${step.join(', ')}]`;
            stepsList.appendChild(listItem);
        });
    }
});