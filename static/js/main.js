/**
 * Основной JavaScript для сайта Атнинской ЦРБ
 */
(function () {
    'use strict';

    const menuToggle = document.getElementById('menuToggle');
    const mainNav = document.getElementById('mainNav');

    if (menuToggle && mainNav) {
        menuToggle.addEventListener('click', function () {
            mainNav.classList.toggle('open');
            menuToggle.classList.toggle('active');
        });

        document.addEventListener('click', function (event) {
            if (!mainNav.contains(event.target) && !menuToggle.contains(event.target)) {
                mainNav.classList.remove('open');
            }
        });
    }

    const dropdownItems = document.querySelectorAll('.has-dropdown > a');
    dropdownItems.forEach(function (link) {
        link.addEventListener('click', function (event) {
            if (window.innerWidth < 768) {
                event.preventDefault();
                const parent = link.parentElement;
                parent.classList.toggle('open');
            }
        });
    });

    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            alert.style.opacity = '0';
            alert.style.transition = 'opacity 0.5s';
            setTimeout(function () {
                alert.remove();
            }, 500);
        }, 5000);
    });

    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('.nav-list a');
    navLinks.forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

    const forms = document.querySelectorAll('form');
    forms.forEach(function (form) {
        form.addEventListener('submit', function () {
            const submitBtn = form.querySelector('[type="submit"]');
            if (submitBtn && !submitBtn.disabled) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Отправка...';
                setTimeout(function () {
                    submitBtn.disabled = false;
                    submitBtn.textContent = submitBtn.dataset.originalText || 'Отправить';
                }, 10000);
            }
        });
    });

    const submitButtons = document.querySelectorAll('[type="submit"]');
    submitButtons.forEach(function (btn) {
        btn.dataset.originalText = btn.textContent;
    });

    function validatePhone(input) {
        const phonePattern = /^[\d\s+\-()]{7,20}$/;
        if (input.value && !phonePattern.test(input.value)) {
            input.setCustomValidity('Введите корректный номер телефона');
        } else {
            input.setCustomValidity('');
        }
    }

    const phoneInputs = document.querySelectorAll('input[name="phone"]');
    phoneInputs.forEach(function (input) {
        input.addEventListener('input', function () {
            validatePhone(input);
        });
    });

    window.addEventListener('resize', function () {
        if (window.innerWidth >= 768 && mainNav) {
            mainNav.classList.remove('open');
            document.querySelectorAll('.has-dropdown.open').forEach(function (item) {
                item.classList.remove('open');
            });
        }
    });
})();
