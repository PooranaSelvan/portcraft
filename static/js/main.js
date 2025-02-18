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


