document.addEventListener('DOMContentLoaded', function() {
    // Calendar functionality
    const calendarDates = document.getElementById('calendarDates');
    const currentMonthElement = document.querySelector('.current-month');
    const prevBtn = document.querySelector('.calendar-nav-btn.prev');
    const nextBtn = document.querySelector('.calendar-nav-btn.next');
    const timeSlotsContainer = document.getElementById('timeSlots');
    const selectedDateDisplay = document.getElementById('selectedDateDisplay');
    const noSlotsMessage = document.getElementById('noSlotsMessage');
    const appointmentSummary = document.getElementById('appointmentSummary');
    const clearSelectionBtn = document.getElementById('clearSelectionBtn');
    const summaryDateElement = document.getElementById('summaryDate');
    const summaryTimeElement = document.getElementById('summaryTime');
    const selectedTimeInput = document.getElementById('selectedTime');
    const selectedDateInput = document.getElementById('selectedDate');
    const appointmentDatetimeInput = document.getElementById('appointmentDatetime');

    let currentDate = new Date();
    let selectedDate = null;
    let selectedTime = null;

    // Available time slots for each day (simulated data)
    const availableTimeSlots = {
        // Format: 'YYYY-MM-DD': [time slots]
        [getDateKey(new Date())]: ['09:00 AM', '10:30 AM', '02:00 PM', '03:30 PM'],
        [getDateKey(addDays(new Date(), 1))]: ['10:00 AM', '11:30 AM', '03:00 PM', '04:30 PM'],
        [getDateKey(addDays(new Date(), 2))]: ['09:30 AM', '11:00 AM', '02:30 PM', '04:00 PM'],
        [getDateKey(addDays(new Date(), 3))]: ['09:00 AM', '10:30 AM', '02:00 PM'],
        [getDateKey(addDays(new Date(), 4))]: ['11:00 AM', '03:30 PM'],
        [getDateKey(addDays(new Date(), 5))]: ['09:30 AM', '02:30 PM', '04:00 PM'],
        [getDateKey(addDays(new Date(), 6))]: [], // No slots on this day
        [getDateKey(addDays(new Date(), 7))]: ['10:00 AM', '02:00 PM', '03:30 PM'],
        [getDateKey(addDays(new Date(), 8))]: ['09:00 AM', '11:00 AM', '03:00 PM'],
        [getDateKey(addDays(new Date(), 9))]: ['10:30 AM', '02:30 PM', '04:30 PM'],
    };

    // Initialize calendar
    renderCalendar(currentDate);

    // Event listeners for calendar navigation
    prevBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() - 1);
        renderCalendar(currentDate);
    });

    nextBtn.addEventListener('click', () => {
        currentDate.setMonth(currentDate.getMonth() + 1);
        renderCalendar(currentDate);
    });

    // Clear selection
    if (clearSelectionBtn) {
        clearSelectionBtn.addEventListener('click', clearSelection);
    }

    function renderCalendar(date) {
        const year = date.getFullYear();
        const month = date.getMonth();
        
        // Update month display
        currentMonthElement.textContent = date.toLocaleDateString('en-US', {
            month: 'long',
            year: 'numeric'
        });

        // Get first day of month
        const firstDay = new Date(year, month, 1);
        const lastDay = new Date(year, month + 1, 0);
        const daysInMonth = lastDay.getDate();
        const startingDay = firstDay.getDay();

        // Clear calendar
        calendarDates.innerHTML = '';

        // Add empty cells for days before the first day of month
        for (let i = 0; i < startingDay; i++) {
            const emptyDay = createCalendarDay('', true);
            calendarDates.appendChild(emptyDay);
        }

        // Add days of the month
        const today = new Date();
        today.setHours(0, 0, 0, 0);

        for (let day = 1; day <= daysInMonth; day++) {
            const currentDay = new Date(year, month, day);
            const dateKey = getDateKey(currentDay);
            const hasSlots = availableTimeSlots[dateKey] && availableTimeSlots[dateKey].length > 0;
            const isPast = currentDay < today;
            const isToday = currentDay.toDateString() === today.toDateString();
            const isSelected = selectedDate && getDateKey(selectedDate) === dateKey;

            const dayElement = createCalendarDay(day, false);
            
            if (isToday) dayElement.classList.add('today');
            if (isSelected) dayElement.classList.add('selected');
            if (isPast) dayElement.classList.add('disabled');
            if (hasSlots && !isPast) dayElement.classList.add('has-slots');

            if (!isPast) {
                dayElement.addEventListener('click', () => selectDate(currentDay));
            }

            calendarDates.appendChild(dayElement);
        }
    }

    function createCalendarDay(dayNumber, isEmpty) {
        const dayElement = document.createElement('div');
        dayElement.className = 'calendar-day' + (isEmpty ? ' empty' : '');
        
        if (!isEmpty) {
            dayElement.innerHTML = `
                <div class="date-number">${dayNumber}</div>
                <div class="available-slots">Slots</div>
            `;
        }
        
        return dayElement;
    }

    function selectDate(date) {
        selectedDate = date;
        selectedDateInput.value = getDateKey(date);
        
        // Update UI
        document.querySelectorAll('.calendar-day.selected').forEach(day => {
            day.classList.remove('selected');
        });
        
        const dateKey = getDateKey(date);
        const calendarDays = calendarDates.querySelectorAll('.calendar-day:not(.empty)');
        calendarDays.forEach((day, index) => {
            const dayNumber = parseInt(day.querySelector('.date-number').textContent);
            const currentDay = new Date(currentDate.getFullYear(), currentDate.getMonth(), dayNumber);
            if (getDateKey(currentDay) === dateKey) {
                day.classList.add('selected');
            }
        });

        // Update selected date display
        const formattedDate = date.toLocaleDateString('en-US', {
            weekday: 'long',
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
        selectedDateDisplay.textContent = formattedDate;

        // Show time slots for selected date
        showTimeSlots(date);
        
        // Clear previous time selection
        selectedTime = null;
        selectedTimeInput.value = '';
        
        // Update appointment summary
        updateAppointmentSummary();
    }

    function showTimeSlots(date) {
        const dateKey = getDateKey(date);
        const slots = availableTimeSlots[dateKey] || [];
        
        // Clear time slots
        timeSlotsContainer.innerHTML = '';
        
        if (slots.length === 0) {
            noSlotsMessage.style.display = 'block';
            timeSlotsContainer.style.display = 'none';
        } else {
            noSlotsMessage.style.display = 'none';
            timeSlotsContainer.style.display = 'grid';
            
            // Create time slot buttons
            slots.forEach(slot => {
                const timeSlotBtn = document.createElement('button');
                timeSlotBtn.type = 'button';
                timeSlotBtn.className = 'time-slot-btn';
                timeSlotBtn.textContent = slot;
                
                // Check if slot is booked (simulated)
                const isBooked = Math.random() < 0.3; // 30% chance a slot is booked
                if (isBooked) {
                    timeSlotBtn.classList.add('booked');
                    timeSlotBtn.disabled = true;
                    timeSlotBtn.title = 'This slot is already booked';
                }
                
                timeSlotBtn.addEventListener('click', () => selectTime(slot, timeSlotBtn));
                timeSlotsContainer.appendChild(timeSlotBtn);
            });
        }
    }

    function selectTime(time, buttonElement) {
        // Clear previous selection
        document.querySelectorAll('.time-slot-btn.selected').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Set new selection
        selectedTime = time;
        buttonElement.classList.add('selected');
        selectedTimeInput.value = time;
        
        // Set full appointment datetime
        if (selectedDate) {
            const [timeStr, period] = time.split(' ');
            let [hours, minutes] = timeStr.split(':').map(Number);
            
            // Convert to 24-hour format
            if (period === 'PM' && hours !== 12) hours += 12;
            if (period === 'AM' && hours === 12) hours = 0;
            
            const appointmentDate = new Date(selectedDate);
            appointmentDate.setHours(hours, minutes, 0, 0);
            
            appointmentDatetimeInput.value = appointmentDate.toISOString();
        }
        
        // Update appointment summary
        updateAppointmentSummary();
    }

    function updateAppointmentSummary() {
        if (selectedDate && selectedTime) {
            const formattedDate = selectedDate.toLocaleDateString('en-US', {
                weekday: 'short',
                month: 'short',
                day: 'numeric',
                year: 'numeric'
            });
            
            summaryDateElement.textContent = formattedDate;
            summaryTimeElement.textContent = selectedTime;
            appointmentSummary.classList.add('show');
        } else {
            summaryDateElement.textContent = 'No date selected';
            summaryTimeElement.textContent = 'No time selected';
            appointmentSummary.classList.remove('show');
        }
    }

    function clearSelection() {
        selectedDate = null;
        selectedTime = null;
        selectedDateInput.value = '';
        selectedTimeInput.value = '';
        appointmentDatetimeInput.value = '';
        
        // Clear UI selections
        document.querySelectorAll('.calendar-day.selected').forEach(day => {
            day.classList.remove('selected');
        });
        
        document.querySelectorAll('.time-slot-btn.selected').forEach(btn => {
            btn.classList.remove('selected');
        });
        
        // Reset displays
        selectedDateDisplay.textContent = 'Today';
        appointmentSummary.classList.remove('show');
        timeSlotsContainer.innerHTML = '';
        noSlotsMessage.style.display = 'none';
        
        // Reset summary
        summaryDateElement.textContent = 'No date selected';
        summaryTimeElement.textContent = 'No time selected';
    }

    // Helper functions
    function getDateKey(date) {
        return date.toISOString().split('T')[0]; // Returns YYYY-MM-DD
    }

    function addDays(date, days) {
        const result = new Date(date);
        result.setDate(result.getDate() + days);
        return result;
    }

    // Initialize with today's date if it has slots
    const todayKey = getDateKey(new Date());
    if (availableTimeSlots[todayKey] && availableTimeSlots[todayKey].length > 0) {
        selectDate(new Date());
    }

    // Form validation and other functionality
    // Character count for textarea
    const topicTextarea = document.getElementById('topic');
    const charCount = document.getElementById('charCount');
    
    if (topicTextarea && charCount) {
        topicTextarea.addEventListener('input', function() {
            const length = this.value.length;
            charCount.textContent = length;
            
            if (length > 500) {
                charCount.style.color = '#dc2626';
                this.style.borderColor = '#dc2626';
            } else {
                charCount.style.color = '#8a8a8a';
                this.style.borderColor = '#e0e0e0';
            }
        });
    }
    
    // Form submission
    const bookingForm = document.getElementById('bookingForm');
    if (bookingForm) {
        bookingForm.addEventListener('submit', function(e) {
            e.preventDefault();
            
            if (!validateForm()) {
                return;
            }
            
            // Show confirmation modal
            showConfirmationModal();
        });
    }
    
    function validateForm() {
        // Basic validation
        const name = document.getElementById('name').value.trim();
        const email = document.getElementById('email').value.trim();
        const phone = document.getElementById('phone').value.trim();
        const topic = document.getElementById('topic').value.trim();
        const terms = document.getElementById('terms').checked;
        
        if (!name || !email || !phone || !topic) {
            alert('Please fill in all required fields.');
            return false;
        }
        
        if (!selectedDate) {
            alert('Please select a date for your consultation.');
            return false;
        }
        
        if (!selectedTime) {
            alert('Please select a time slot for your consultation.');
            return false;
        }
        
        if (!terms) {
            alert('Please agree to the terms and conditions.');
            return false;
        }
        
        // Email validation
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(email)) {
            alert('Please enter a valid email address.');
            return false;
        }
        
        return true;
    }
    
    // Modal functionality
    const modal = document.getElementById('confirmationModal');
    const modalCloseBtns = document.querySelectorAll('.modal-close, .btn-modal-close');
    
    function showConfirmationModal() {
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }
    
    modalCloseBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
            window.location.href = '/services';
        });
    });
    
    // Close modal when clicking outside
    if (modal) {
        modal.addEventListener('click', function(e) {
            if (e.target === modal) {
                modal.style.display = 'none';
                document.body.style.overflow = 'auto';
                window.location.href = '/services';
            }
        });
    }
});