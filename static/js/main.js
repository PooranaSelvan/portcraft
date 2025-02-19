// Import jQuery (assuming it's included in your HTML)
// or include a CDN link like: <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script> in your HTML file

$(document).ready(() => {
  // Make elements draggable
  $(".draggable").draggable({
    containment: "#portfolio-editor",
    cursor: "move",
  })

  // Save portfolio
  $("#save-portfolio").click(() => {
    var portfolioContent = $("#portfolio-editor").html()
    $.ajax({
      url: "/save-portfolio",
      type: "POST",
      contentType: "application/json",
      data: JSON.stringify({ content: portfolioContent }),
      success: (response) => {
        if (response.success) {
          alert("Portfolio saved successfully!")
        } else {
          alert("Error saving portfolio.")
        }
      },
    })
  })
document.getElementById('preview-portfolio').addEventListener('click', function() {
    const portfolioData = {
        name: document.getElementById('name').value.trim(),
        about: document.getElementById('about').value.trim(),
        skills: document.getElementById('skills').value.trim(),
        work: document.getElementById('work').value.trim(),
        projects: document.getElementById('projects').value.trim(),
        contact: document.getElementById('contact').value.trim(),
        social_links: document.getElementById('social_links') ? document.getElementById('social_links').value.trim() : '',
        photo: document.getElementById('photo') ? document.getElementById('photo').value.trim() : ''
    };

    fetch('/preview-portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(portfolioData)
    })
    .then(response => response.text())  // Get the HTML response
    .then(html => {
        document.body.innerHTML = html;  // Load the preview page
    })
    .catch(error => console.error('Error:', error));
});

ddocument.getElementById('preview-portfolio').addEventListener('click', function() {
    const portfolioData = {
        name: document.getElementById('name').value.trim(),
        about: document.getElementById('about').value.trim(),
        skills: document.getElementById('skills').value.trim(),
        work: document.getElementById('work').value.trim(),
        projects: document.getElementById('projects').value.trim(),
        contact: document.getElementById('contact').value.trim(),
        social_links: document.getElementById('social-links').value.trim()
    };

    const photoInput = document.getElementById('photo');
    if (photoInput.files.length > 0) {
        const reader = new FileReader();
        reader.onload = function(event) {
            portfolioData.photo = event.target.result;
            fetchPreview(portfolioData);
        };
        reader.readAsDataURL(photoInput.files[0]);
    } else {
        fetchPreview(portfolioData);
    }
});

function fetchPreview(portfolioData) {
    fetch('/preview-portfolio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(portfolioData)
    })
    .then(response => response.json())
    .then(data => {
        const newTab = window.open();
        newTab.document.open();
        newTab.document.write(generatePreviewHTML(data));
        newTab.document.close();
    })
    .catch(error => console.error('Error:', error));
}

function generatePreviewHTML(data) {
    return `
        <html>
        <head>
            <title>Portfolio Preview</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; padding: 20px; }
                .container { display: flex; }
                .sidebar { width: 250px; padding: 20px; background: #f4f4f4; }
                .content { flex-grow: 1; padding: 20px; }
                .profile-photo { width: 100px; height: 100px; border-radius: 50%; }
            </style>
        </head>
        <body>
            <div class="container">
                <aside class="sidebar">
                    ${data.photo ? `<img src="${data.photo}" class="profile-photo" alt="Profile Photo">` : ""}
                    <h2>${data.name}</h2>
                    <p>${data.contact}</p>
                    <h3>Social Media</h3>
                    <ul>
                        ${data.social_links.split(',').map(link => `<li><a href="${link.trim()}" target="_blank">${link.trim()}</a></li>`).join('')}
                    </ul>
                </aside>
                <main class="content">
                    <section>
                        <h2>About Me</h2>
                        <p>${data.about}</p>
                    </section>
                    <section>
                        <h2>Projects</h2>
                        <p>${data.projects}</p>
                    </section>
                    <section>
                        <h2>Skills</h2>
                        <p>${data.skills}</p>
                    </section>
                    <section>
                        <h2>Work Experience</h2>
                        <p>${data.work}</p>
                    </section>
                </main>
            </div>
        </body>
        </html>
    `;
}

