document.getElementById('checkEssayBtn').addEventListener('click', function() {
    const text = document.getElementById('essayInput').value;
    if (text) {
      fetch('/essay_assistant', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'text=' + encodeURIComponent(text),
      })
      .then(response => response.json())
      .then(data => {
        if (data.structure_suggestions) {
          let feedback = `<h6>Structure Tips:</h6>
                          <ul>
                            <li>Introduction: ${data.structure_suggestions.introduction}</li>
                            <li>Body: ${data.structure_suggestions.body}</li>
                            <li>Conclusion: ${data.structure_suggestions.conclusion}</li>
                          </ul>`;
          feedback += `<h6>Vocabulary Suggestions:</h6><ul>`;
          data.vocab_suggestions.forEach(suggestion => {
            feedback += `<li>${suggestion}</li>`;
          });
          feedback += `</ul><p><strong>Cohesiveness Score:</strong> ${data.cohesiveness_score.toFixed(2)}</p>`;
          document.getElementById('essayFeedback').innerHTML = feedback;
        } else {
          document.getElementById('essayFeedback').innerText = 'Error: ' + (data.error || 'An error occurred');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        document.getElementById('essayFeedback').innerText = 'An error occurred while processing your request.';
      });
    } else {
      document.getElementById('essayFeedback').innerText = 'Please enter some text for analysis.';
    }
  });