document.getElementById('checkGrammarBtn').addEventListener('click', function() {
    const text = document.getElementById('grammarInput').value;
    if (text) {
      fetch('/grammar_correction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: 'text=' + encodeURIComponent(text),
      })
      .then(response => response.json())
      .then(data => {
        if (data.corrected_text) {
          document.getElementById('correctedText').innerText = 'Corrected Text: ' + data.corrected_text;
        } else {
          document.getElementById('correctedText').innerText = 'Error: ' + (data.error || 'An error occurred');
        }
      })
      .catch(error => {
        console.error('Error:', error);
        document.getElementById('correctedText').innerText = 'An error occurred while processing your request.';
      });
    } else {
      document.getElementById('correctedText').innerText = 'Please enter some text for correction.';
    }
  });