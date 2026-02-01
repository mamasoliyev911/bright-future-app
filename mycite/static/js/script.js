async function saveLead() {
    const leadData = {
        name: document.getElementById('lName').value,
        age: document.getElementById('lAge').value,
        school: document.getElementById('lSchool').value,
        course: document.getElementById('lCourse').value,
        source: document.getElementById('lSource').value,
        teacher: document.getElementById('lTeacher').value,
        has_trial: document.getElementById('lTrial').value === 'ha'
    };

    // Django APIga POST so'rov yuborish
    const response = await fetch('http://127.0.0.1:8000/api/leads/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            // 'X-CSRFToken': getCookie('csrftoken') // Django xavfsizligi uchun
        },
        body: JSON.stringify(leadData)
    });

    if (response.ok) {
        renderLeads(); // Ro'yxatni yangilash
        closeModal();
    }
}