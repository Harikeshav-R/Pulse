import { useState } from 'react'
import './VisitCalendar.css'

const dayNames = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const monthNames = ["January", "February", "March", "April", "May", "June",
  "July", "August", "September", "October", "November", "December"];

export function VisitCalendar() {
  const [currentDate, setCurrentDate] = useState(new Date(2026, 2, 1)); // March 2026

  const prevMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() - 1, 1));
  };
  
  const nextMonth = () => {
    setCurrentDate(new Date(currentDate.getFullYear(), currentDate.getMonth() + 1, 1));
  };

  const generateDays = () => {
    const year = currentDate.getFullYear();
    const month = currentDate.getMonth();
    
    // Find the first day of the month (0 = Sun, 1 = Mon, ..., 6 = Sat)
    const firstDay = new Date(year, month, 1).getDay();
    
    // We want Monday as the first day of the week (0)
    // If firstDay is 0 (Sun), shift it to 6.
    const startOffset = firstDay === 0 ? 6 : firstDay - 1;
    
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    const daysInPrevMonth = new Date(year, month, 0).getDate();
    
    const days = [];
    
    // Previous month's trailing days
    for (let i = 0; i < startOffset; i++) {
        days.unshift({
            date: daysInPrevMonth - i,
            disabled: true,
            id: `prev-${i}`
        });
    }
    
    // Current month's days
    for (let i = 1; i <= daysInMonth; i++) {
        days.push({
            date: i,
            disabled: false,
            id: `curr-${i}`
        });
    }
    
    // Next month's leading days to complete 42 cells (6 weeks) or 35 (5 weeks)
    const totalCells = days.length > 35 ? 42 : 35;
    let nextDay = 1;
    while (days.length < totalCells) {
        days.push({
            date: nextDay++,
            disabled: true,
            id: `next-${nextDay}`
        });
    }
    
    return days;
  };

  const displayDays = generateDays();

  return (
    <div className="calendar-wrapper">
      <div className="projects-section-header">
        <p>Visit Calendar</p>
      </div>
      <div className="calendar-container">
        <div className="calendar-header">
          <button onClick={prevMonth}>
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15 19l-7-7 7-7" />
            </svg>
          </button>
          <div>
            <h1>{monthNames[currentDate.getMonth()]}</h1>
            <p>{currentDate.getFullYear()}</p>
          </div>
          <button onClick={nextMonth}>
            <svg width="24" height="24" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
            </svg>
          </button>
        </div>

        <div className="calendar">
          {dayNames.map(name => (
            <span key={name} className="day-name">{name}</span>
          ))}

          {displayDays.map(day => (
            <div key={day.id} className={`day ${day.disabled ? 'day--disabled' : ''}`}>
              {day.date}
            </div>
          ))}

          <section className="task task--warning">
            Protocol Submissions
          </section>
          
          <section className="task task--danger">
            Site Initiation Visit
          </section>
          
          <section className="task task--primary">
            Patient 003 Dosing Week 1
            <div className="task__detail">
              <h2>Patient 003 Dosing Week 1</h2>
              <p>15-17th {monthNames[currentDate.getMonth()]}</p>
            </div>
          </section>
          
          <section className="task task--info">
            Cohort A Safety Review
          </section>
        </div>
      </div>
    </div>
  );
}
