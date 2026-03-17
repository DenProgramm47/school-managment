import axios from 'axios';

const API = axios.create({
  baseURL: 'http://localhost:5000/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const getStudents = (params = {}) => {
  const cleanParams = {};
  
  if (params.fio && params.fio.trim() !== '') {
    cleanParams.fio = params.fio.trim();
  }
  
  if (params.course && params.course.toString().trim() !== '') {
    cleanParams.course = params.course.toString().trim();
  }
  
  if (params.site && params.site.trim() !== '') {
    cleanParams.site = params.site.trim();
  }
  
  if (params.liter && params.liter.toString().trim() !== '') {
    cleanParams.liter = params.liter.toString().trim();
  }
  
  return API.get('/students', { params: cleanParams });
};

export default API;