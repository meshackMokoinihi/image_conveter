document.getElementById('convertFeature').addEventListener('click', function() {
  document.getElementById('uploadDiv').style.display = 'block';
  document.getElementById('grammarDiv').style.display = 'none';
  document.getElementById('essayDiv').style.display = 'none';
  document.getElementById('webpage_to_pdf_div').style.display = 'none';
});

document.getElementById('grammarCorrection').addEventListener('click', function() {
  document.getElementById('uploadDiv').style.display = 'none';
  document.getElementById('grammarDiv').style.display = 'block';
  document.getElementById('essayDiv').style.display = 'none';
  document.getElementById('webpage_to_pdf_div').style.display = 'none';
});

document.getElementById('essayAssistant').addEventListener('click', function() {
  document.getElementById('uploadDiv').style.display = 'none';
  document.getElementById('grammarDiv').style.display = 'none';
  document.getElementById('essayDiv').style.display = 'block';
  document.getElementById('webpage_to_pdf_div').style.display = 'none';
});

document.getElementById('webpage_to_pdf').addEventListener('click', function() {
  document.getElementById('uploadDiv').style.display = 'none';
  document.getElementById('grammarDiv').style.display = 'none';
  document.getElementById('essayDiv').style.display = 'none';
  document.getElementById('webpage_to_pdf_div').style.display = 'block';
});