<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>My Profile</span>
      </div>
    </template>
    <el-form :model="form" label-width="120px" style="max-width: 500px">
      <el-form-item label="Username">
        <el-input v-model="form.username"></el-input>
      </el-form-item>
      <el-form-item label="New Password">
        <el-input v-model="form.password" type="password" placeholder="Leave blank to keep current password"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="handleUpdate">Update Profile</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
import { getCurrentUser, updateCurrentUser } from '../services/api';

const form = reactive({
  username: '',
  password: '',
});

const originalUsername = ref('');

onMounted(async () => {
  try {
    const user = await getCurrentUser();
    form.username = user.username;
    originalUsername.value = user.username;
  } catch (error) {
    console.error('Failed to load profile:', error);
    ElMessage.error('Failed to load your profile data.');
  }
});

const handleUpdate = async () => {
  const payload = {};
  if (form.username && form.username !== originalUsername.value) {
    payload.username = form.username;
  }
  if (form.password) {
    payload.password = form.password;
  }

  if (Object.keys(payload).length === 0) {
    ElMessage.info('No changes to update.');
    return;
  }

  try {
    await updateCurrentUser(payload);
    ElMessage.success('Profile updated successfully! You may need to log in again if you changed your username.');
    // Optionally, refresh data or handle logout if username changed
    if (payload.username) {
        // A full reload might be best to ensure clean state
        window.location.reload();
    }
  } catch (error) {
    console.error('Failed to update profile:', error);
    ElMessage.error(error.response?.data?.detail || 'Failed to update profile.');
  }
};
</script>