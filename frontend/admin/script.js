const API_URL = 'https://clinic-booking-system-opre.onrender.com:3001/api';

document.addEventListener('DOMContentLoaded', loadAppointments);

async function loadAppointments() {
    const response = await fetch(`${API_URL}/admin/appointments`);
    const appointments = await response.json();
    const tableBody = document.querySelector('#appointmentsTable tbody');
    tableBody.innerHTML = '';

    appointments.forEach(appointment => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${appointment.name}</td>
            <td>${appointment.phone}</td>
            <td>${appointment.gender}</td>
            <td>${appointment.age}</td>
            <td>${appointment.date}</td>
            <td>${appointment.time}</td>
            <td class="status-${appointment.status === 'معلق' ? 'pending' : appointment.status === 'مؤكد' ? 'confirmed' : 'cancelled'}">
                ${appointment.status}
            </td>
            <td>
                <button class="confirm-button" onclick="updateAppointmentStatus('${appointment.id}', 'مؤكد')">تأكيد</button>
                <button class="cancel-button" onclick="updateAppointmentStatus('${appointment.id}', 'ملغى')">إلغاء</button>
            </td>
        `;
        tableBody.appendChild(row);
    });
}

async function updateAppointmentStatus(id, status) {
    const response = await fetch(`${API_URL}/admin/appointments/${id}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
    });

    if (response.ok) {
        loadAppointments();
    } else {
        alert('حدث خطأ أثناء تحديث حالة الموعد!');
    }
}
