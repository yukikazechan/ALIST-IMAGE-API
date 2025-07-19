<template>
  <el-card>
    <template #header>
      <div class="card-header">
        <span>User Management</span>
      </div>
    </template>
    <el-table :data="users" style="width: 100%">
      <el-table-column prop="id" label="ID" width="80"></el-table-column>
      <el-table-column prop="username" label="Username"></el-table-column>
      <el-table-column prop="is_admin" label="Admin" width="100">
        <template #default="scope">
          <el-tag :type="scope.row.is_admin ? 'success' : 'info'">
            {{ scope.row.is_admin ? 'Yes' : 'No' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="Actions" width="120">
        <template #default="scope">
          <el-popconfirm
            title="Are you sure to delete this user?"
            @confirm="handleDelete(scope.row.id)"
            :disabled="scope.row.is_admin"
          >
            <template #reference>
              <el-button
                size="small"
                type="danger"
                :disabled="scope.row.is_admin"
              >
                Delete
              </el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>
  </el-card>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { ElMessage } from 'element-plus';
// We will create these API functions in the next step
import { getUsers, deleteUser } from '../services/api'; 

const users = ref([]);

const fetchUsers = async () => {
  try {
    users.value = await getUsers();
  } catch (error) {
    console.error('Failed to fetch users:', error);
    ElMessage.error('Failed to load users.');
  }
};

const handleDelete = async (userId) => {
  try {
    await deleteUser(userId);
    ElMessage.success('User deleted successfully.');
    fetchUsers(); // Refresh the list
  } catch (error) {
    console.error('Failed to delete user:', error);
    ElMessage.error('Failed to delete user.');
  }
};

onMounted(() => {
  fetchUsers();
});
</script>