// // booking.js - Fixed version with proper scoping
// let currentDate, selectedDate, selectedTime;

// document.addEventListener('DOMContentLoaded', function() {
//     // Initialize calendar state
//     currentDate = new Date();
//     selectedDate = null;
//     selectedTime = null;
    
//     // Initialize calendar
//     initCalendar();
    
//     // Navigation buttons
//     document.querySelector('.calendar-nav-btn.prev').addEventListener('click', function() {
//         currentDate.setMonth(currentDate.getMonth() - 1);
//         updateCalendar();
//     });
    
//     document.querySelector('.calendar-nav-btn.next').addEventListener('click', function() {
//         currentDate.setMonth(currentDate.getMonth() + 1);
//         updateCalendar();
//     });
    
//     // Form submission
// // In booking.js, REMOVE or COMMENT OUT this:
// // document.getElementById('bookingForm').addEventListener('submit', function(e) {
// //     e.preventDefault();
// //     
// //     if (!selectedDate || !selectedTime) {
// //         alert('Please select a date and time for your appointment');
// //         return;
// //     }
// //     
// //     // Create appointment datetime
// //     const appointmentDatetime = `${selectedDate}T${selectedTime}:00`;
// //     document.getElementById('appointmentDatetime').value = appointmentDatetime;
// //     
// //     // Submit form via AJAX
// //     submitBookingForm(this);
// // });
//     // Character counter for topic textarea
//     const topicTextarea = document.getElementById('topic');
//     const charCount = document.getElementById('charCount');
    
//     topicTextarea.addEventListener('input', function() {
//         charCount.textContent = this.value.length;
//     });
    
//     // File upload handling
//     const fileInput = document.getElementById('documents');
//     const fileList = document.getElementById('fileList');
    
//     fileInput.addEventListener('change', function() {
//         fileList.innerHTML = '';
//         Array.from(this.files).forEach(file => {
//             const fileItem = document.createElement('div');
//             fileItem.className = 'file-item';
//             fileItem.innerHTML = `
//                 <i class="fas fa-file"></i>
//                 <span>${file.name} (${(file.size / 1024).toFixed(2)} KB)</span>
//                 <button type="button" class="remove-file"><i class="fas fa-times"></i></button>
//             `;
//             fileItem.querySelector('.remove-file').addEventListener('click', function() {
//                 fileItem.remove();
//                 // Also remove from file input
//                 const dt = new DataTransfer();
//                 const files = fileInput.files;
                
//                 for (let i = 0; i < files.length; i++) {
//                     const file = files[i];
//                     if (file.name !== fileItem.querySelector('span').textContent.split(' (')[0]) {
//                         dt.items.add(file);
//                     }
//                 }
                
//                 fileInput.files = dt.files;
//             });
//             fileList.appendChild(fileItem);
//         });
//     });
    
//     // Clear selection button
//     document.getElementById('clearSelectionBtn').addEventListener('click', function() {
//         clearSelection();
//     });
    
//     // Test initial API call
//     console.log('Testing API connection...');
//     testAPI();
// });

// // Make functions globally accessible
// window.initCalendar = initCalendar;
// window.updateCalendar = updateCalendar;
// window.checkMonthAvailability = checkMonthAvailability;
// window.loadAvailableSlots = loadAvailableSlots;
// window.selectDate = selectDate;
// window.selectTime = selectTime;
// window.clearSelection = clearSelection;
// // // window.submitBookingForm = submitBookingForm;
// // window.showConfirmationModal = showConfirmationModal;
// window.addToCalendar = addToCalendar;
// window.getEndTime = getEndTime;
// window.validateForm = validateForm;

// function initCalendar() {
//     console.log('Initializing calendar...');
//     updateCalendar();
//     // Load today's slots
//     const today = new Date().toISOString().split('T')[0];
//     loadAvailableSlots(today);
// }

// function updateCalendar() {
//     console.log('Updating calendar for:', currentDate);
//     const monthNames = ["January", "February", "March", "April", "May", "June",
//         "July", "August", "September", "October", "November", "December"];
    
//     // Update month display
//     document.querySelector('.current-month').textContent = 
//         `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
    
//     // Generate calendar dates
//     generateCalendarDates(currentDate.getFullYear(), currentDate.getMonth());
// }

// function generateCalendarDates(year, month) {
//     const calendarDates = document.getElementById('calendarDates');
//     calendarDates.innerHTML = '';
    
//     // Get first day of month
//     const firstDay = new Date(year, month, 1);
//     const lastDay = new Date(year, month + 1, 0);
//     const daysInMonth = lastDay.getDate();
    
//     // Get day of week for first day (0 = Sunday)
//     const startingDay = firstDay.getDay();
    
//     // Add empty cells for days before first day
//     for (let i = 0; i < startingDay; i++) {
//         const emptyCell = document.createElement('div');
//         emptyCell.className = 'calendar-date empty';
//         calendarDates.appendChild(emptyCell);
//     }
    
//     // Add cells for each day
//     const today = new Date().toISOString().split('T')[0];
    
//     for (let day = 1; day <= daysInMonth; day++) {
//         const dateCell = document.createElement('div');
//         dateCell.className = 'calendar-date';
//         dateCell.textContent = day;
        
//         const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
//         dateCell.dataset.date = dateStr;
        
//         // Check if it's today
//         if (dateStr === today) {
//             dateCell.classList.add('today');
//         }
        
//         // Check if it's selected
//         if (selectedDate === dateStr) {
//             dateCell.classList.add('selected');
//         }
        
//         // Check if it's in the past
//         const cellDate = new Date(dateStr);
//         const now = new Date();
//         now.setHours(0, 0, 0, 0);
        
//         if (cellDate < now) {
//             dateCell.classList.add('past');
//         } else {
//             // Add click event for future dates
//             dateCell.addEventListener('click', function() {
//                 selectDate(dateStr);
//             });
//         }
        
//         calendarDates.appendChild(dateCell);
//     }
    
//     // Check availability for each date
//     checkMonthAvailability(year, month);
// }

// async function checkMonthAvailability(year, month) {
//     console.log(`Checking availability for ${year}-${month + 1}`);
//     try {
//         const response = await fetch(`/api/date-availability/?year=${year}&month=${month + 1}`);
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
//         const data = await response.json();
//         console.log('Availability data:', data);
        
//         data.dates.forEach(dateInfo => {
//             const dateCell = document.querySelector(`[data-date="${dateInfo.date}"]`);
//             if (dateCell && !dateCell.classList.contains('past')) {
//                 if (dateInfo.has_availability) {
//                     dateCell.classList.add('available');
//                     dateCell.style.cursor = 'pointer';
//                 } else {
//                     dateCell.classList.add('unavailable');
//                     dateCell.style.cursor = 'not-allowed';
//                 }
//             }
//         });
//     } catch (error) {
//         console.error('Error checking availability:', error);
//         // Mark all dates as unavailable on error
//         document.querySelectorAll('.calendar-date:not(.past):not(.empty)').forEach(cell => {
//             cell.classList.add('unavailable');
//             cell.style.cursor = 'not-allowed';
//         });
//     }
// }

// // Update loadAvailableSlots function
// async function loadAvailableSlots(dateStr) {
//     console.log(`Loading slots for date: ${dateStr}`);
    
//     // Get selected duration - FIXED VERSION
//     let durationMinutes;
//     const durationInput = document.querySelector('[name="duration_minutes"]');
    
//     if (durationInput && durationInput.value) {
//         durationMinutes = durationInput.value;
//     } else {
//         // Fallback: Extract from URL or use default
//         const urlPath = window.location.pathname;
//         const match = urlPath.match(/booking\/(\d+)-min\//);
//         if (match && match[1]) {
//             durationMinutes = match[1];
//         } else {
//             durationMinutes = '45'; // Default
//         }
//     }
    
//     try {
//         const response = await fetch(`/api/available-slots/?date=${dateStr}&duration=${durationMinutes}`);
//         // ... rest of the function remains the same 
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
//         const data = await response.json();
//         console.log('Available slots data:', data);
        
//         const timeSlots = document.getElementById('timeSlots');
//         const noSlotsMessage = document.getElementById('noSlotsMessage');
        
//         timeSlots.innerHTML = '';
        
//         if (data.available_slots && data.available_slots.length > 0) {
//             noSlotsMessage.style.display = 'none';
            
//             // Sort slots by time
//             data.available_slots.sort((a, b) => a.start_time.localeCompare(b.start_time));
            
//             data.available_slots.forEach(slot => {
//                 const slotButton = document.createElement('button');
//                 slotButton.type = 'button';
//                 slotButton.className = 'time-slot';
//                 slotButton.innerHTML = `
//                     <div class="slot-content">
//                         <span class="time-display">${slot.display || `${slot.start_time} - ${slot.end_time}`}</span>
//                         <span class="duration-badge">${slot.duration} min</span>
//                     </div>
//                 `;
//                 slotButton.dataset.time = slot.start_time;
//                 slotButton.dataset.slotId = slot.id;
//                 slotButton.dataset.duration = slot.duration;
                
//                 // Check if time is in the past for today
//                 const now = new Date();
//                 const today = now.toISOString().split('T')[0];
//                 const [hours, minutes] = slot.start_time.split(':');
//                 const slotTime = new Date();
//                 slotTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);
                
//                 if (dateStr === today && slotTime < now) {
//                     slotButton.classList.add('past-slot');
//                     slotButton.disabled = true;
//                     slotButton.title = 'This time has already passed';
//                 } else {
//                     if (selectedTime === slot.start_time && selectedDate === dateStr) {
//                         slotButton.classList.add('selected');
//                     }
                    
//                     slotButton.addEventListener('click', function() {
//                         selectTime(dateStr, slot.start_time, slot.id);
//                     });
//                 }
                
//                 timeSlots.appendChild(slotButton);
//             });
//         } else {
//             noSlotsMessage.style.display = 'block';
//             noSlotsMessage.innerHTML = `
//                 <i class="fas fa-calendar-times"></i>
//                 <p>${data.is_today && data.current_time ? `No available slots for today (${data.current_time}).` : 'No available slots for this date.'} Please select another date.</p>
//             `;
//         }
//     } catch (error) {
//         console.error('Error loading slots:', error);
//         const noSlotsMessage = document.getElementById('noSlotsMessage');
//         noSlotsMessage.style.display = 'block';
//         noSlotsMessage.innerHTML = `
//             <i class="fas fa-exclamation-triangle"></i>
//             <p>Error loading time slots. Please try again.</p>
//         `;
//     }
// }

// // Update checkMonthAvailability function
// async function checkMonthAvailability(year, month) {
//     console.log(`Checking availability for ${year}-${month + 1}`);
    
//     // Get selected duration - FIXED VERSION
//     let durationMinutes;
//     const durationInput = document.querySelector('[name="duration_minutes"]');
    
//     if (durationInput && durationInput.value) {
//         durationMinutes = durationInput.value;
//     } else {
//         // Fallback
//         const urlPath = window.location.pathname;
//         const match = urlPath.match(/booking\/(\d+)-min\//);
//         if (match && match[1]) {
//             durationMinutes = match[1];
//         } else {
//             durationMinutes = '45';
//         }
//     }
    
//     try {
//         const response = await fetch(`/api/date-availability/?year=${year}&month=${month + 1}&duration=${durationMinutes}`);
//         // ... rest of the function remains the same
//         if (!response.ok) {
//             throw new Error(`HTTP error! status: ${response.status}`);
//         }
//         const data = await response.json();
//         console.log('Availability data:', data);
        
//         data.dates.forEach(dateInfo => {
//             const dateCell = document.querySelector(`[data-date="${dateInfo.date}"]`);
//             if (dateCell && !dateCell.classList.contains('past')) {
//                 if (dateInfo.has_availability) {
//                     dateCell.classList.add('available');
//                     dateCell.style.cursor = 'pointer';
//                 } else {
//                     dateCell.classList.add('unavailable');
//                     dateCell.style.cursor = 'not-allowed';
//                     dateCell.title = 'No available slots for selected duration';
//                 }
//             }
//         });
//     } catch (error) {
//         console.error('Error checking availability:', error);
//     }
// }

// // Update selectTime function
// function selectTime(dateStr, timeStr, slotId = null) {
//     console.log('Time selected:', timeStr, 'Slot ID:', slotId);
//     selectedTime = timeStr;
    
//     if (slotId) {
//         document.querySelector('[name="selected_slot_id"]').value = slotId;
//     }
    
//     // Update UI
//     document.querySelectorAll('.time-slot.selected').forEach(el => {
//         el.classList.remove('selected');
//     });
    
//     document.querySelectorAll('.time-slot').forEach(el => {
//         if (el.dataset.time === timeStr) {
//             el.classList.add('selected');
//         }
//     });
    
//     // Update summary with duration
//     const timeDisplay = document.getElementById('summaryTime');
//     const [hours, minutes] = timeStr.split(':');
//     const timeObj = new Date();
//     timeObj.setHours(hours, minutes);
    
//     const duration = document.querySelector('[name="duration_minutes"]').value;
//     timeDisplay.textContent = `${timeObj.toLocaleTimeString('en-US', { 
//         hour: 'numeric', 
//         minute: '2-digit',
//         hour12: true 
//     })} (${duration} min)`;
    
//     // Update hidden fields
//     document.getElementById('selectedDate').value = dateStr;
//     document.getElementById('selectedTime').value = timeStr;
    
//     // Show appointment summary
//     const summary = document.getElementById('appointmentSummary');
//     summary.style.display = 'block';
//     summary.style.opacity = '1';
// }

// // Add event listener for package selection to refresh calendar
// document.addEventListener('DOMContentLoaded', function() {
//     // When user clicks on different package cards, reload calendar
//     document.querySelectorAll('.btn-select').forEach(button => {
//         button.addEventListener('click', function(e) {
//             // Don't prevent default - let the link work
//             // But we'll add a small delay to allow URL change
//             setTimeout(() => {
//                 location.reload();
//             }, 100);
//         });
//     });
    
//     // Also reload when package is changed via URL parameter
//     const urlParams = new URLSearchParams(window.location.search);
//     if (urlParams.has('duration')) {
//         // Calendar will auto-refresh on page load
//     }
// });

// // Fix the selectDate function
// function selectDate(dateStr) {
//     console.log('Date selected:', dateStr);
    
//     // Update selected date
//     selectedDate = dateStr;
    
//     // Update UI
//     document.querySelectorAll('.calendar-date.selected').forEach(el => {
//         el.classList.remove('selected');
//     });
    
//     const selectedCell = document.querySelector(`[data-date="${dateStr}"]`);
//     if (selectedCell) {
//         selectedCell.classList.add('selected');
//     }
    
//     // Update display
//     updateDateDisplay(dateStr);
    
//     // Load available slots for selected date
//     loadAvailableSlots(dateStr);
// }

// // Add this helper function
// function updateDateDisplay(dateStr) {
//     const dateDisplay = document.getElementById('selectedDateDisplay');
//     const dateObj = new Date(dateStr);
//     const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
//     dateDisplay.textContent = dateObj.toLocaleDateString('en-US', options);
    
//     // Update summary
//     document.getElementById('summaryDate').textContent = 
//         dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
// }

// // Update the calendar generation to use proper event listeners
// function generateCalendarDates(year, month) {
//     const calendarDates = document.getElementById('calendarDates');
//     calendarDates.innerHTML = '';
    
//     // Get first day of month
//     const firstDay = new Date(year, month, 1);
//     const lastDay = new Date(year, month + 1, 0);
//     const daysInMonth = lastDay.getDate();
    
//     // Get day of week for first day (0 = Sunday)
//     const startingDay = firstDay.getDay();
    
//     // Add empty cells for days before first day
//     for (let i = 0; i < startingDay; i++) {
//         const emptyCell = document.createElement('div');
//         emptyCell.className = 'calendar-date empty';
//         calendarDates.appendChild(emptyCell);
//     }
    
//     // Add cells for each day
//     const today = new Date().toISOString().split('T')[0];
    
//     for (let day = 1; day <= daysInMonth; day++) {
//         const dateCell = document.createElement('div');
//         dateCell.className = 'calendar-date';
//         dateCell.textContent = day;
        
//         const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
//         dateCell.dataset.date = dateStr;
        
//         // Check if it's today
//         if (dateStr === today) {
//             dateCell.classList.add('today');
//         }
        
//         // Check if it's selected
//         if (selectedDate === dateStr) {
//             dateCell.classList.add('selected');
//         }
        
//         // Check if it's in the past
//         const cellDate = new Date(dateStr);
//         const now = new Date();
//         now.setHours(0, 0, 0, 0);
        
//         if (cellDate < now) {
//             dateCell.classList.add('past');
//             dateCell.style.cursor = 'not-allowed';
//             dateCell.title = 'Past date - not available';
//         } else {
//             // Add click event for future dates
//             dateCell.addEventListener('click', function() {
//                 selectDate(dateStr);
//             });
//             dateCell.style.cursor = 'pointer';
//         }
        
//         calendarDates.appendChild(dateCell);
//     }
    
//     // Check availability for each date
//     checkMonthAvailability(year, month);
// }

// // Update the time slot display
// function updateTimeSlotsDisplay(slots) {
//     const timeSlots = document.getElementById('timeSlots');
//     const noSlotsMessage = document.getElementById('noSlotsMessage');
    
//     timeSlots.innerHTML = '';
    
//     if (slots && slots.length > 0) {
//         noSlotsMessage.style.display = 'none';
        
//         // Sort slots by time
//         slots.sort((a, b) => a.start_time.localeCompare(b.start_time));
        
//         slots.forEach(slot => {
//             const slotButton = document.createElement('button');
//             slotButton.type = 'button';
//             slotButton.className = 'time-slot';
//             slotButton.innerHTML = `
//                 <span class="time-display">${slot.display || `${slot.start_time} - ${slot.end_time}`}</span>
//                 <span class="duration-badge">${slot.duration} min</span>
//             `;
//             slotButton.dataset.time = slot.start_time;
//             slotButton.dataset.slotId = slot.id;
//             slotButton.dataset.duration = slot.duration;
            
//             if (selectedTime === slot.start_time && selectedDate === selectedDate) {
//                 slotButton.classList.add('selected');
//             }
            
//             slotButton.addEventListener('click', function() {
//                 selectTime(selectedDate, slot.start_time, slot.id);
//             });
            
//             timeSlots.appendChild(slotButton);
//         });
//     } else {
//         noSlotsMessage.style.display = 'block';
//         noSlotsMessage.innerHTML = `
//             <i class="fas fa-calendar-times"></i>
//             <p>No available slots for ${selectedDate ? new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) : 'this date'}. Please select another date.</p>
//         `;
//     }
// }
// function clearSelection() {
//     console.log('Clearing selection');
//     selectedDate = null;
//     selectedTime = null;
    
//     // Update UI
//     document.querySelectorAll('.calendar-date.selected').forEach(el => {
//         el.classList.remove('selected');
//     });
    
//     document.querySelectorAll('.time-slot.selected').forEach(el => {
//         el.classList.remove('selected');
//     });
    
//     // Reset summary
//     document.getElementById('selectedDateDisplay').textContent = 'Today';
//     document.getElementById('summaryDate').textContent = 'No date selected';
//     document.getElementById('summaryTime').textContent = 'No time selected';
    
//     // Clear hidden fields
//     document.getElementById('selectedDate').value = '';
//     document.getElementById('selectedTime').value = '';
//     document.getElementById('appointmentDatetime').value = '';
    
//     // Hide summary
//     const summary = document.getElementById('appointmentSummary');
//     summary.style.display = 'none';
//     summary.style.opacity = '0';
// } // Only one closing brace here

// booking.js - Fixed version with proper scoping
let currentDate, selectedDate, selectedTime;

document.addEventListener('DOMContentLoaded', function() {
    // Initialize calendar state
    currentDate = new Date();
    selectedDate = null;
    selectedTime = null;
    
    // Initialize calendar
    initCalendar();
    
    // Navigation buttons
    document.querySelector('.calendar-nav-btn.prev').addEventListener('click', function() {
        currentDate.setMonth(currentDate.getMonth() - 1);
        updateCalendar();
    });
    
    document.querySelector('.calendar-nav-btn.next').addEventListener('click', function() {
        currentDate.setMonth(currentDate.getMonth() + 1);
        updateCalendar();
    });
    
    // Form submission
    document.getElementById('bookingForm').addEventListener('submit', function(e) {
        e.preventDefault();
        
        if (!selectedDate || !selectedTime) {
            alert('Please select a date and time for your appointment');
            return;
        }
        
        // Create appointment datetime
        const appointmentDatetime = `${selectedDate}T${selectedTime}:00`;
        document.getElementById('appointmentDatetime').value = appointmentDatetime;
        
        // Submit form via AJAX
        submitBookingForm(this);
    });
    
    // Character counter for topic textarea
    const topicTextarea = document.getElementById('topic');
    const charCount = document.getElementById('charCount');
    
    topicTextarea.addEventListener('input', function() {
        charCount.textContent = this.value.length;
    });
    
    // File upload handling
    const fileInput = document.getElementById('documents');
    const fileList = document.getElementById('fileList');
    
    fileInput.addEventListener('change', function() {
        fileList.innerHTML = '';
        Array.from(this.files).forEach(file => {
            const fileItem = document.createElement('div');
            fileItem.className = 'file-item';
            fileItem.innerHTML = `
                <i class="fas fa-file"></i>
                <span>${file.name} (${(file.size / 1024).toFixed(2)} KB)</span>
                <button type="button" class="remove-file"><i class="fas fa-times"></i></button>
            `;
            fileItem.querySelector('.remove-file').addEventListener('click', function() {
                fileItem.remove();
                // Also remove from file input
                const dt = new DataTransfer();
                const files = fileInput.files;
                
                for (let i = 0; i < files.length; i++) {
                    const file = files[i];
                    if (file.name !== fileItem.querySelector('span').textContent.split(' (')[0]) {
                        dt.items.add(file);
                    }
                }
                
                fileInput.files = dt.files;
            });
            fileList.appendChild(fileItem);
        });
    });
    
    // Clear selection button
    document.getElementById('clearSelectionBtn').addEventListener('click', function() {
        clearSelection();
    });
    
    // Test initial API call
    console.log('Testing API connection...');
    testAPI();
});

// Make functions globally accessible
window.initCalendar = initCalendar;
window.updateCalendar = updateCalendar;
window.checkMonthAvailability = checkMonthAvailability;
window.loadAvailableSlots = loadAvailableSlots;
window.selectDate = selectDate;
window.selectTime = selectTime;
window.clearSelection = clearSelection;
window.submitBookingForm = submitBookingForm;
window.showConfirmationModal = showConfirmationModal;
window.addToCalendar = addToCalendar;
window.getEndTime = getEndTime;
window.validateForm = validateForm;

function initCalendar() {
    console.log('Initializing calendar...');
    updateCalendar();
    // Load today's slots
    const today = new Date().toISOString().split('T')[0];
    loadAvailableSlots(today);
}

function updateCalendar() {
    console.log('Updating calendar for:', currentDate);
    const monthNames = ["January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December"];
    
    // Update month display
    document.querySelector('.current-month').textContent = 
        `${monthNames[currentDate.getMonth()]} ${currentDate.getFullYear()}`;
    
    // Generate calendar dates
    generateCalendarDates(currentDate.getFullYear(), currentDate.getMonth());
}

function generateCalendarDates(year, month) {
    const calendarDates = document.getElementById('calendarDates');
    calendarDates.innerHTML = '';
    
    // Get first day of month
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    
    // Get day of week for first day (0 = Sunday)
    const startingDay = firstDay.getDay();
    
    // Add empty cells for days before first day
    for (let i = 0; i < startingDay; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.className = 'calendar-date empty';
        calendarDates.appendChild(emptyCell);
    }
    
    // Add cells for each day
    const today = new Date().toISOString().split('T')[0];
    
    for (let day = 1; day <= daysInMonth; day++) {
        const dateCell = document.createElement('div');
        dateCell.className = 'calendar-date';
        dateCell.textContent = day;
        
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        dateCell.dataset.date = dateStr;
        
        // Check if it's today
        if (dateStr === today) {
            dateCell.classList.add('today');
        }
        
        // Check if it's selected
        if (selectedDate === dateStr) {
            dateCell.classList.add('selected');
        }
        
        // Check if it's in the past
        const cellDate = new Date(dateStr);
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        
        if (cellDate < now) {
            dateCell.classList.add('past');
        } else {
            // Add click event for future dates
            dateCell.addEventListener('click', function() {
                selectDate(dateStr);
            });
        }
        
        calendarDates.appendChild(dateCell);
    }
    
    // Check availability for each date
    checkMonthAvailability(year, month);
}

async function checkMonthAvailability(year, month) {
    console.log(`Checking availability for ${year}-${month + 1}`);
    try {
        const response = await fetch(`/api/date-availability/?year=${year}&month=${month + 1}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Availability data:', data);
        
        data.dates.forEach(dateInfo => {
            const dateCell = document.querySelector(`[data-date="${dateInfo.date}"]`);
            if (dateCell && !dateCell.classList.contains('past')) {
                if (dateInfo.has_availability) {
                    dateCell.classList.add('available');
                    dateCell.style.cursor = 'pointer';
                } else {
                    dateCell.classList.add('unavailable');
                    dateCell.style.cursor = 'not-allowed';
                }
            }
        });
    } catch (error) {
        console.error('Error checking availability:', error);
        // Mark all dates as unavailable on error
        document.querySelectorAll('.calendar-date:not(.past):not(.empty)').forEach(cell => {
            cell.classList.add('unavailable');
            cell.style.cursor = 'not-allowed';
        });
    }
}

// Update loadAvailableSlots function
// Update loadAvailableSlots function in booking.js
async function loadAvailableSlots(dateStr) {
    console.log(`Loading slots for date: ${dateStr}`);
    
    // Get selected duration
    const duration = document.querySelector('[name="duration"]').value;
    const durationMinutes = duration.replace('-min', '');
    
    try {
        const response = await fetch(`/api/available-slots/?date=${dateStr}&duration=${durationMinutes}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Available slots data:', data);
        
        const timeSlots = document.getElementById('timeSlots');
        const noSlotsMessage = document.getElementById('noSlotsMessage');
        
        timeSlots.innerHTML = '';
        
        if (data.available_slots && data.available_slots.length > 0) {
            noSlotsMessage.style.display = 'none';
            
            // Sort slots by time
            data.available_slots.sort((a, b) => a.start_time.localeCompare(b.start_time));
            
            data.available_slots.forEach(slot => {
                const slotButton = document.createElement('button');
                slotButton.type = 'button';
                slotButton.className = 'time-slot';
                slotButton.innerHTML = `
                    <div class="slot-content">
                        <span class="time-display">${slot.display || `${slot.start_time} - ${slot.end_time}`}</span>
                        <span class="duration-badge">${slot.duration} min</span>
                    </div>
                `;
                slotButton.dataset.time = slot.start_time;
                slotButton.dataset.slotId = slot.id;
                slotButton.dataset.duration = slot.duration;
                
                // Check if time is in the past for today
                const now = new Date();
                const today = now.toISOString().split('T')[0];
                const [hours, minutes] = slot.start_time.split(':');
                const slotTime = new Date();
                slotTime.setHours(parseInt(hours), parseInt(minutes), 0, 0);
                
                if (dateStr === today && slotTime < now) {
                    slotButton.classList.add('past-slot');
                    slotButton.disabled = true;
                    slotButton.title = 'This time has already passed';
                } else {
                    if (selectedTime === slot.start_time && selectedDate === dateStr) {
                        slotButton.classList.add('selected');
                    }
                    
                    slotButton.addEventListener('click', function() {
                        selectTime(dateStr, slot.start_time, slot.id);
                    });
                }
                
                timeSlots.appendChild(slotButton);
            });
        } else {
            noSlotsMessage.style.display = 'block';
            noSlotsMessage.innerHTML = `
                <i class="fas fa-calendar-times"></i>
                <p>${data.is_today && data.current_time ? `No available slots for today (${data.current_time}).` : 'No available slots for this date.'} Please select another date.</p>
            `;
        }
    } catch (error) {
        console.error('Error loading slots:', error);
        const noSlotsMessage = document.getElementById('noSlotsMessage');
        noSlotsMessage.style.display = 'block';
        noSlotsMessage.innerHTML = `
            <i class="fas fa-exclamation-triangle"></i>
            <p>Error loading time slots. Please try again.</p>
        `;
    }
}
// Update checkMonthAvailability function
async function checkMonthAvailability(year, month) {
    console.log(`Checking availability for ${year}-${month + 1}`);
    
    // Get selected duration
    const duration = document.querySelector('[name="duration"]').value;
    const durationMinutes = duration.replace('-min', '');
    
    try {
        const response = await fetch(`/api/date-availability/?year=${year}&month=${month + 1}&duration=${durationMinutes}`);
        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }
        const data = await response.json();
        console.log('Availability data:', data);
        
        data.dates.forEach(dateInfo => {
            const dateCell = document.querySelector(`[data-date="${dateInfo.date}"]`);
            if (dateCell && !dateCell.classList.contains('past')) {
                if (dateInfo.has_availability) {
                    dateCell.classList.add('available');
                    dateCell.style.cursor = 'pointer';
                } else {
                    dateCell.classList.add('unavailable');
                    dateCell.style.cursor = 'not-allowed';
                    dateCell.title = 'No available slots for selected duration';
                }
            }
        });
    } catch (error) {
        console.error('Error checking availability:', error);
    }
}

// Update selectTime function
function selectTime(dateStr, timeStr, slotId = null) {
    console.log('Time selected:', timeStr, 'Slot ID:', slotId);
    selectedTime = timeStr;
    
    if (slotId) {
        document.querySelector('[name="selected_slot_id"]').value = slotId;
    }
    
    // Update UI
    document.querySelectorAll('.time-slot.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    document.querySelectorAll('.time-slot').forEach(el => {
        if (el.dataset.time === timeStr) {
            el.classList.add('selected');
        }
    });
    
    // Update summary with duration
    const timeDisplay = document.getElementById('summaryTime');
    const [hours, minutes] = timeStr.split(':');
    const timeObj = new Date();
    timeObj.setHours(hours, minutes);
    
    const duration = document.querySelector('[name="duration_minutes"]').value;
    timeDisplay.textContent = `${timeObj.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
    })} (${duration} min)`;
    
    // Update hidden fields
    document.getElementById('selectedDate').value = dateStr;
    document.getElementById('selectedTime').value = timeStr;
    
    // Show appointment summary
    const summary = document.getElementById('appointmentSummary');
    summary.style.display = 'block';
    summary.style.opacity = '1';
}

// Add event listener for package selection to refresh calendar
document.addEventListener('DOMContentLoaded', function() {
    // When user clicks on different package cards, reload calendar
    document.querySelectorAll('.btn-select').forEach(button => {
        button.addEventListener('click', function(e) {
            // Don't prevent default - let the link work
            // But we'll add a small delay to allow URL change
            setTimeout(() => {
                location.reload();
            }, 100);
        });
    });
    
    // Also reload when package is changed via URL parameter
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.has('duration')) {
        // Calendar will auto-refresh on page load
    }
});

// Fix the selectDate function - Add this at the top
function selectDate(dateStr) {
    console.log('Date selected:', dateStr);
    
    // Update selected date
    selectedDate = dateStr;
    
    // Update UI
    document.querySelectorAll('.calendar-date.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    const selectedCell = document.querySelector(`[data-date="${dateStr}"]`);
    if (selectedCell) {
        selectedCell.classList.add('selected');
    }
    
    // Update display
    updateDateDisplay(dateStr);
    
    // Load available slots for selected date
    loadAvailableSlots(dateStr);
}

// Add this helper function
function updateDateDisplay(dateStr) {
    const dateDisplay = document.getElementById('selectedDateDisplay');
    const dateObj = new Date(dateStr);
    const options = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
    dateDisplay.textContent = dateObj.toLocaleDateString('en-US', options);
    
    // Update summary
    document.getElementById('summaryDate').textContent = 
        dateObj.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
}

// Update the calendar generation to use proper event listeners
function generateCalendarDates(year, month) {
    const calendarDates = document.getElementById('calendarDates');
    calendarDates.innerHTML = '';
    
    // Get first day of month
    const firstDay = new Date(year, month, 1);
    const lastDay = new Date(year, month + 1, 0);
    const daysInMonth = lastDay.getDate();
    
    // Get day of week for first day (0 = Sunday)
    const startingDay = firstDay.getDay();
    
    // Add empty cells for days before first day
    for (let i = 0; i < startingDay; i++) {
        const emptyCell = document.createElement('div');
        emptyCell.className = 'calendar-date empty';
        calendarDates.appendChild(emptyCell);
    }
    
    // Add cells for each day
    const today = new Date().toISOString().split('T')[0];
    
    for (let day = 1; day <= daysInMonth; day++) {
        const dateCell = document.createElement('div');
        dateCell.className = 'calendar-date';
        dateCell.textContent = day;
        
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        dateCell.dataset.date = dateStr;
        
        // Check if it's today
        if (dateStr === today) {
            dateCell.classList.add('today');
        }
        
        // Check if it's selected
        if (selectedDate === dateStr) {
            dateCell.classList.add('selected');
        }
        
        // Check if it's in the past
        const cellDate = new Date(dateStr);
        const now = new Date();
        now.setHours(0, 0, 0, 0);
        
        if (cellDate < now) {
            dateCell.classList.add('past');
            dateCell.style.cursor = 'not-allowed';
            dateCell.title = 'Past date - not available';
        } else {
            // Add click event for future dates
            dateCell.addEventListener('click', function() {
                selectDate(dateStr);
            });
            dateCell.style.cursor = 'pointer';
        }
        
        calendarDates.appendChild(dateCell);
    }
    
    // Check availability for each date
    checkMonthAvailability(year, month);
}

// Update the time slot display
function updateTimeSlotsDisplay(slots) {
    const timeSlots = document.getElementById('timeSlots');
    const noSlotsMessage = document.getElementById('noSlotsMessage');
    
    timeSlots.innerHTML = '';
    
    if (slots && slots.length > 0) {
        noSlotsMessage.style.display = 'none';
        
        // Sort slots by time
        slots.sort((a, b) => a.start_time.localeCompare(b.start_time));
        
        slots.forEach(slot => {
            const slotButton = document.createElement('button');
            slotButton.type = 'button';
            slotButton.className = 'time-slot';
            slotButton.innerHTML = `
                <span class="time-display">${slot.display || `${slot.start_time} - ${slot.end_time}`}</span>
                <span class="duration-badge">${slot.duration} min</span>
            `;
            slotButton.dataset.time = slot.start_time;
            slotButton.dataset.slotId = slot.id;
            slotButton.dataset.duration = slot.duration;
            
            if (selectedTime === slot.start_time && selectedDate === selectedDate) {
                slotButton.classList.add('selected');
            }
            
            slotButton.addEventListener('click', function() {
                selectTime(selectedDate, slot.start_time, slot.id);
            });
            
            timeSlots.appendChild(slotButton);
        });
    } else {
        noSlotsMessage.style.display = 'block';
        noSlotsMessage.innerHTML = `
            <i class="fas fa-calendar-times"></i>
            <p>No available slots for ${selectedDate ? new Date(selectedDate).toLocaleDateString('en-US', { weekday: 'long', month: 'long', day: 'numeric' }) : 'this date'}. Please select another date.</p>
        `;
    }
}

function selectTime(dateStr, timeStr) {
    console.log('Time selected:', timeStr);
    selectedTime = timeStr;
    
    // Update UI
    document.querySelectorAll('.time-slot.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    document.querySelectorAll('.time-slot').forEach(el => {
        if (el.dataset.time === timeStr) {
            el.classList.add('selected');
        }
    });
    
    // Update summary
    const timeDisplay = document.getElementById('summaryTime');
    const [hours, minutes] = timeStr.split(':');
    const timeObj = new Date();
    timeObj.setHours(hours, minutes);
    timeDisplay.textContent = timeObj.toLocaleTimeString('en-US', { 
        hour: 'numeric', 
        minute: '2-digit',
        hour12: true 
    });
    
    // Update hidden fields
    document.getElementById('selectedDate').value = dateStr;
    document.getElementById('selectedTime').value = timeStr;
    
    // Show appointment summary
    const summary = document.getElementById('appointmentSummary');
    summary.style.display = 'block';
    summary.style.opacity = '1';
}

function clearSelection() {
    console.log('Clearing selection');
    selectedDate = null;
    selectedTime = null;
    
    // Update UI
    document.querySelectorAll('.calendar-date.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    document.querySelectorAll('.time-slot.selected').forEach(el => {
        el.classList.remove('selected');
    });
    
    // Reset summary
    document.getElementById('selectedDateDisplay').textContent = 'Today';
    document.getElementById('summaryDate').textContent = 'No date selected';
    document.getElementById('summaryTime').textContent = 'No time selected';
    
    // Clear hidden fields
    document.getElementById('selectedDate').value = '';
    document.getElementById('selectedTime').value = '';
    document.getElementById('appointmentDatetime').value = '';
    
    // Hide summary
    const summary = document.getElementById('appointmentSummary');
    summary.style.display = 'none';
    summary.style.opacity = '0';
}
async function submitBookingForm(form) {
    const formData = new FormData(form);
    const submitButton = form.querySelector('.btn-submit');
    
    // Validate required fields
    if (!validateForm()) {
        return;
    }
    
    // Disable submit button
    submitButton.disabled = true;
    submitButton.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Processing...';
    
    try {
        const response = await fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
            }
        });
        
        const result = await response.json();
        console.log('Submission result:', result);
        
        if (result.success) {
            // Show success modal with booking details
            showConfirmationModal(
                result.booking_id,
                selectedDate,
                selectedTime
            );
            
            // Reset form
            form.reset();
            clearSelection();
            
            // Update character count
            document.getElementById('charCount').textContent = '0';
            document.getElementById('fileList').innerHTML = '';
            
        } else {
            alert('Error: ' + result.error);
        }
    } catch (error) {
        alert('An error occurred. Please try again.');
        console.error('Submission error:', error);
    } finally {
        // Re-enable submit button
        submitButton.disabled = false;
        submitButton.innerHTML = '<i class="fas fa-calendar-check"></i> Confirm & Schedule Consultation';
    }
}

function validateForm() {
    // Check if date and time are selected
    if (!selectedDate || !selectedTime) {
        alert('Please select a date and time for your appointment');
        return false;
    }
    
    // Check required fields
    const name = document.getElementById('name').value.trim();
    const email = document.getElementById('email').value.trim();
    const phone = document.getElementById('phone').value.trim();
    const topic = document.getElementById('topic').value.trim();
    
    if (!name || !email || !phone || !topic) {
        alert('Please fill in all required fields (marked with *)');
        return false;
    }
    
    // Check email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        alert('Please enter a valid email address');
        return false;
    }
    
    // Check terms agreement
    const terms = document.getElementById('terms');
    if (!terms.checked) {
        alert('Please agree to the Terms of Service and Privacy Policy');
        return false;
    }
    
    return true;
}
function showConfirmationModal(bookingId, appointmentDate, appointmentTime) {
    const modal = document.getElementById('confirmationModal');
    
    // Get selected date and time
    const dateStr = selectedDate;
    const timeStr = selectedTime;
    
    if (dateStr && timeStr) {
        // Format date nicely
        const dateObj = new Date(dateStr);
        const formattedDate = dateObj.toLocaleDateString('en-US', { 
            weekday: 'long', 
            year: 'numeric', 
            month: 'long', 
            day: 'numeric' 
        });
        
        // Format time nicely
        const [hours, minutes] = timeStr.split(':');
        const timeObj = new Date();
        timeObj.setHours(hours, minutes);
        const formattedTime = timeObj.toLocaleTimeString('en-US', { 
            hour: 'numeric', 
            minute: '2-digit',
            hour12: true 
        });
        
        // Create appointment datetime for calendar
        const appointmentDatetime = `${dateStr}T${timeStr}:00`;
        
        // Store in hidden field
        const appointmentInput = modal.querySelector('#appointmentDatetime');
        if (!appointmentInput) {
            // Create hidden input if it doesn't exist
            const input = document.createElement('input');
            input.type = 'hidden';
            input.id = 'appointmentDatetime';
            input.value = appointmentDatetime;
            modal.querySelector('.modal-content').appendChild(input);
        } else {
            appointmentInput.value = appointmentDatetime;
        }
        
        // Update summary in modal (if elements exist)
        const dateElement = modal.querySelector('#summaryDate');
        const timeElement = modal.querySelector('#summaryTime');
        
        if (dateElement) dateElement.textContent = formattedDate;
        if (timeElement) timeElement.textContent = formattedTime;
    }
    
    // Add booking ID if provided
    if (bookingId) {
        // Clear any existing booking ID element
        document.querySelectorAll('.summary-item.booking-id').forEach(el => el.remove());
        
        const bookingSummary = modal.querySelector('.booking-summary');
        if (bookingSummary) {
            const bookingIdElement = document.createElement('div');
            bookingIdElement.className = 'summary-item booking-id';
            bookingIdElement.innerHTML = `
                <strong>Booking ID:</strong>
                <span>${bookingId}</span>
            `;
            bookingSummary.appendChild(bookingIdElement);
        }
    }
    
    modal.style.display = 'flex';
    modal.style.alignItems = 'center';
    modal.style.justifyContent = 'center';
    
    // Close modal handlers
    const closeModal = () => {
        modal.style.display = 'none';
        // Optionally reload or redirect
        // location.reload();
    };
    
    modal.querySelector('.modal-close')?.addEventListener('click', closeModal);
    modal.querySelector('.btn-modal-close')?.addEventListener('click', () => {
        modal.style.display = 'none';
        window.location.href = '/services';
    });
    
    modal.querySelector('.btn-modal-calendar')?.addEventListener('click', () => {
        addToCalendar();
    });
    
    // Remove old event listeners to prevent duplicates
    modal.querySelector('.modal-close')?.removeEventListener('click', closeModal);
    modal.querySelector('.btn-modal-close')?.removeEventListener('click', () => {
        modal.style.display = 'none';
        window.location.href = '/services';
    });
    modal.querySelector('.btn-modal-calendar')?.removeEventListener('click', () => {
        addToCalendar();
    });
    
    // Add new event listeners
    modal.querySelector('.modal-close')?.addEventListener('click', closeModal);
    modal.querySelector('.btn-modal-close')?.addEventListener('click', () => {
        modal.style.display = 'none';
        window.location.href = '/services';
    });
    modal.querySelector('.btn-modal-calendar')?.addEventListener('click', () => {
        addToCalendar();
    });
}
function addToCalendar() {
    // Get appointment datetime from hidden input in modal
    const modal = document.getElementById('confirmationModal');
    const appointmentInput = modal.querySelector('#appointmentDatetime');
    
    if (!appointmentInput || !appointmentInput.value) {
        // Try to get from form if not in modal
        const formAppointment = document.getElementById('appointmentDatetime');
        if (formAppointment && formAppointment.value) {
            appointmentDatetime = formAppointment.value;
        } else {
            alert('No appointment time selected');
            return;
        }
    }
    
    const appointmentDatetime = appointmentInput.value;
    const title = document.querySelector('.page-title')?.textContent || 'Consultation with KP RegTech';
    const description = document.querySelector('.page-subtitle')?.textContent || 'Professional consultation session';
    
    // Calculate end time
    const duration = document.querySelector('[name="duration_minutes"]')?.value || '60';
    const durationMinutes = parseInt(duration);
    
    // Parse start time
    const startDate = new Date(appointmentDatetime);
    const endDate = new Date(startDate.getTime() + durationMinutes * 60000);
    
    // Format dates for ICS
    function formatDateForICS(date) {
        return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
    }
    
    // Create ICS file content
    const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//KP RegTech//Consultation Booking//EN
CALSCALE:GREGORIAN
BEGIN:VEVENT
UID:${Date.now()}kpregtech@gmail.com
DTSTAMP:${formatDateForICS(new Date())}
DTSTART:${formatDateForICS(startDate)}
DTEND:${formatDateForICS(endDate)}
SUMMARY:${title}
DESCRIPTION:${description}\\n\\nBooking details will be sent via email.
LOCATION:Consultation with KP RegTech (Mode: ${document.querySelector('[name="mode"]:checked')?.value || 'video'})
STATUS:CONFIRMED
SEQUENCE:0
BEGIN:VALARM
TRIGGER:-PT15M
ACTION:DISPLAY
DESCRIPTION:Reminder: Consultation starts in 15 minutes
END:VALARM
END:VEVENT
END:VCALENDAR`;
    
    // Create and trigger download
    const blob = new Blob([icsContent], { type: 'text/calendar;charset=utf-8' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `consultation-${startDate.toISOString().split('T')[0]}.ics`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
    
    // Optional: Show confirmation
    alert('Calendar event downloaded. You can now import it into your calendar.');
}
function getEndTime(startTime) {
    const start = new Date(startTime);
    const duration = parseInt(document.querySelector('[name="duration_minutes"]').value);
    const end = new Date(start.getTime() + duration * 60000);
    
    return end.toISOString().replace(/[-:]/g, '').split('.')[0];
}

function testAPI() {
    const today = new Date().toISOString().split('T')[0];
    console.log('Testing API for date:', today);
    
    fetch(`/api/available-slots/?date=${today}`)
        .then(response => response.json())
        .then(data => {
            console.log('API test successful:', data);
            if (data.available_slots && data.available_slots.length > 0) {
                console.log(`${data.available_slots.length} slots available today`);
            } else {
                console.log('No slots available today');
            }
        })
        .catch(error => console.error('API test failed:', error));
}