import React, { useState, useEffect } from 'react';
import { getStudents } from './api';
import './App.scss';

function App() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filters, setFilters] = useState({
    fio: '',
    course: '',
    site: '',
    liter: ''
  });

  const loadStudents = async (filterParams = {}) => {
    setLoading(true);
    try {
      const response = await getStudents(filterParams);
      if (response.data && response.data.data) {
        setStudents(response.data.data);
      } else {
        setStudents([]);
      }
    } catch (error) {
      console.error('Ошибка загрузки:', error);
      setStudents([]);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadStudents();
  }, []);

  const handleFilterChange = (e) => {
    const { name, value } = e.target;
    const newFilters = { ...filters, [name]: value };
    setFilters(newFilters);
    
    clearTimeout(window.filterTimeout);
    window.filterTimeout = setTimeout(() => {
      loadStudents(newFilters);
    }, 300);
  };

  const resetFilters = () => {
    const emptyFilters = { fio: '', course: '', site: '', liter: '' };
    setFilters(emptyFilters);
    loadStudents(emptyFilters);
  };

  return (
    <div className="app">
      <header className="header">
        <h1>📚 Школьная система</h1>
      </header>

      <div className="container">
        <div className="filters-block">
          <h3>Фильтры</h3>
          
          <div className="filter-group">
            <label>ФИО:</label>
            <input
              type="text"
              name="fio"
              value={filters.fio}
              onChange={handleFilterChange}
              placeholder="Введите ФИО"
            />
          </div>

          <div className="filter-group">
            <label>Класс:</label>
            <select
              name="course"
              value={filters.course}
              onChange={handleFilterChange}
            >
              <option value="">Все</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
              <option value="6">6</option>
              <option value="7">7</option>
              <option value="8">8</option>
              <option value="9">9</option>
              <option value="10">10</option>
              <option value="11">11</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Литера:</label>
            <select
              name="liter"
              value={filters.liter}
              onChange={handleFilterChange}
            >
              <option value="">Все</option>
              <option value="1">1</option>
              <option value="2">2</option>
              <option value="3">3</option>
              <option value="4">4</option>
              <option value="5">5</option>
              <option value="6">6</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Корпус:</label>
            <select
              name="site"
              value={filters.site}
              onChange={handleFilterChange}
            >
              <option value="">Все</option>
              <option value="ВП">ВП</option>
              <option value="АЗ">АЗ</option>
              <option value="С">С</option>
            </select>
          </div>

          <button className="reset-btn" onClick={resetFilters}>
            Сбросить
          </button>

          <div className="count-info">
            Найдено: <strong>{students.length}</strong>
          </div>
        </div>

        <div className="students-block">
          {loading ? (
            <div className="loading">Загрузка...</div>
          ) : students.length === 0 ? (
            <div className="empty">Ученики не найдены</div>
          ) : (
            <div className="students-grid">
              {students.map((student) => (
                <div key={student.id} className="student-card">
                  <div className="card-header">
                    <span className="student-id">#{student.id_student}</span>
                    <span className={`status ${student.status === 'Учится' ? 'status-ok' : 'status-no'}`}>
                      {student.status}
                    </span>
                  </div>
                  
                  <h3 className="student-fio">{student.fio}</h3>
                  
                  <div className="card-info">
                    <div className="info-row">
                      <span className="label">Класс:</span>
                      <span className="value">{student.course}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Литера:</span>
                      <span className="value">{student.liter || '-'}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Корпус:</span>
                      <span className="value">{student.site}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Уровень:</span>
                      <span className="value">{student.level}</span>
                    </div>
                    <div className="info-row">
                      <span className="label">Начало:</span>
                      <span className="value">
                        {student.date_start ? new Date(student.date_start).toLocaleDateString('ru-RU') : '-'}
                      </span>
                    </div>
                    {student.status !== 'Учится' && student.date_end && (
                      <div className="info-row info-row-end">
                        <span className="label">Окончание:</span>
                        <span className="value value-end">
                          {new Date(student.date_end).toLocaleDateString('ru-RU')}
                        </span>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

export default App;