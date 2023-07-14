const usernameField = document.querySelector('#usernameField');
const feedbackArea = document.querySelector('.invalid-feedback');
const emailField = document.querySelector('#emailField');
const emailFeedbackArea = document.querySelector('.emailFeedbackArea');
const usernameSuccessOutput = document.querySelector('.usernameSuccessOutput');
const emailSuccessOutput = document.querySelector('.emailSuccessOutput');
const showPasswordToggle = document.querySelector('.showPasswordToggle');
const passwordField = document.querySelector('#passwordField');
const submitBtn = document.querySelector('.submit-btn');

// submitBtn.disabled = true;

const handleToggleInput = (e) => {
  if (showPasswordToggle.textContent === 'SHOW') {
    showPasswordToggle.textContent = 'HIDE';

    passwordField.setAttribute("type", "text");
  } else {
    showPasswordToggle.textContent = 'SHOW';
    passwordField.setAttribute("type", "password");

  }
};

showPasswordToggle.addEventListener('click', handleToggleInput);



emailField.addEventListener('keyup', (e) => {
  const emailVal = e.target.value;
  emailSuccessOutput.textContent = `Checking ${emailVal}`;
  emailSuccessOutput.style.display = 'block';


  emailField.classList.remove('is-invalid');
  emailFeedbackArea.style.display = 'none';



  if (emailVal.length >= 0) {
    fetch('/authentication/validate_email', {
      body: JSON.stringify({ email: emailVal }),
      method: 'POST'
    })
      .then((res) => res.json())
      .then((data) => {
        console.log('data', data);
        emailSuccessOutput.style.display = 'none';
        if (data.email_error) {
          // submitBtn.setAttribute('disabled', 'disabled');
          submitBtn.disabled = true;
          emailField.classList.add('is-invalid');
          emailFeedbackArea.style.display = 'block';
          emailFeedbackArea.innerHTML = `<p>${data.email_error}</p>`;
        } else {
          submitBtn.removeAttribute('disabled');
        }
      });
  }
});
usernameField.addEventListener('keyup', (e) => {
  const usernameVal = e.target.value;
  usernameSuccessOutput.textContent = `Checking ${usernameVal}`;
  usernameSuccessOutput.style.display = 'block';


  usernameField.classList.remove('is-invalid');
  feedbackArea.style.display = 'none';

  if (usernameVal.length >= 0) {
    fetch('/authentication/validate_username', {
      body: JSON.stringify({ username: usernameVal }),
      method: 'POST'
    })
      .then((res) => res.json())
      .then((data) => {
        console.log('data', data);
        usernameSuccessOutput.style.display = 'none';
        if (data.username_error) {
          submitBtn.disabled = true;
          usernameField.classList.add('is-invalid');
          feedbackArea.style.display = 'block';
          feedbackArea.innerHTML = `<p>${data.username_error}</p>`;
        } else {
          submitBtn.removeAttribute('disabled');
        }
      });
  }
});
