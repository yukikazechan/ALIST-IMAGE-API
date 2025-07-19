<template>
  <div class="login-container">
    <el-card class="login-card">
      <template #header>
        <div class="card-header">
          <span>{{ isRegister ? 'Register' : 'Login' }}</span>
        </div>
      </template>
      <el-form :model="form" label-width="80px">
        <el-form-item label="Username">
          <el-input v-model="form.username"></el-input>
        </el-form-item>
        <el-form-item label="Password">
          <el-input v-model="form.password" type="password"></el-input>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSubmit">{{ isRegister ? 'Register' : 'Login' }}</el-button>
        </el-form-item>
      </el-form>
      <div class="switch-auth">
        <el-button link @click="isRegister = !isRegister">
          {{ isRegister ? 'Already have an account? Login' : "Don't have an account? Register" }}
        </el-button>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue';
import { ElMessage } from 'element-plus';
import { apiClient } from '../services/api'; // Assuming apiClient is exported from api.js

const emit = defineEmits(['authenticated']);
const isRegister = ref(false);
const form = reactive({
  username: '',
  password: '',
});

const handleSubmit = async () => {
  if (!form.username || !form.password) {
    ElMessage.error('Username and password are required.');
    return;
  }

  try {
    if (isRegister.value) {
      // Register
      await apiClient.post('/users/', { username: form.username, password: form.password });
      ElMessage.success('Registration successful! Please login.');
      isRegister.value = false; // Switch to login form
    } else {
      // Login
      const formData = new URLSearchParams();
      formData.append('username', form.username);
      formData.append('password', form.password);

      const response = await apiClient.post('/token', formData, {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      });
      
      const token = response.data.access_token;
      localStorage.setItem('token', token);
      emit('authenticated');
    }
  } catch (error) {
    console.error('Authentication error:', error);
    ElMessage.error(error.response?.data?.detail || 'An error occurred.');
  }
};
</script>

<style scoped>
.login-container {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 100vh;
}
.login-card {
  width: 400px;
}
.card-header {
  text-align: center;
  font-size: 1.5rem;
}
.switch-auth {
  text-align: center;
  margin-top: 1rem;
}
</style>