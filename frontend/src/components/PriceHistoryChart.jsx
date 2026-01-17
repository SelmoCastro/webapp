import React from 'react';
import {
    Chart as ChartJS,
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend,
} from 'chart.js';
import { Line } from 'react-chartjs-2';

ChartJS.register(
    CategoryScale,
    LinearScale,
    PointElement,
    LineElement,
    Title,
    Tooltip,
    Legend
);

const PriceHistoryChart = ({ history }) => {
    // history: array de objetos { price, timestamp }

    // Ordenar cronologicamente
    const sortedHistory = [...history].sort((a, b) => new Date(a.timestamp) - new Date(b.timestamp));

    // Preparar labels e dados
    const labels = sortedHistory.map(item => {
        const date = new Date(item.timestamp);
        return date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' });
    });

    const dataPoints = sortedHistory.map(item => item.price);

    const data = {
        labels,
        datasets: [
            {
                label: 'Histórico de Preço (R$)',
                data: dataPoints,
                borderColor: 'rgb(53, 162, 235)',
                backgroundColor: 'rgba(53, 162, 235, 0.5)',
                tension: 0.1,
            },
        ],
    };

    const options = {
        responsive: true,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: 'Variação de Preço',
            },
        },
        scales: {
            y: {
                beginAtZero: false, // Preços raramente vão a zero, melhor ajustar a escala
            }
        }
    };

    return <Line options={options} data={data} />;
};

export default PriceHistoryChart;
