const API_URL = 'https://clinic-booking-system-opre.onrender.com:3001/api';

document.getElementById('bookingForm').addEventListener('submit', async function (e) {
    e.preventDefault();

    const data = {
        name: document.getElementById('name').value,
        phone: document.getElementById('phone').value,
        gender: document.getElementById('gender').value,
        age: document.getElementById('age').value,
        date: document.getElementById('date').value,
        time: document.getElementById('time').value
    };

    const response = await fetch(`${API_URL}/book`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(data),
    });

    const result = await response.json();
    if (response.ok) {
        const waitingTimeResponse = await fetch(`${API_URL}/waiting-time`);
        const waitingTimeResult = await waitingTimeResponse.json();

        document.getElementById('confirmationMessage').innerHTML = `
            تم حجز الموعد بنجاح!<br>
            زمن المقابلة المتوقع: ${waitingTimeResult.waiting_time_minutes} دقيقة.
        `;
        document.getElementById('confirmationMessage').style.display = 'block';

        setTimeout(() => {
            document.getElementById('confirmationMessage').style.display = 'none';
        }, 5000);

        document.getElementById('bookingForm').reset();
    } else {
        alert(result.error || 'حدث خطأ أثناء حجز الموعد!');
    }
});
