import axios from 'axios';

export const login = async (username, password) => {
  const form = new FormData();
  form.append('username', username);
  form.append('password', password);

  const response = await axios.post('http://localhost:8000/login', form, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });

  return response.data;
};
