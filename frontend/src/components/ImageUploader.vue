<template>
  <el-card class="uploader-card">
    <template #header>
      <div class="card-header">
        <span>Add New Images</span>
      </div>
    </template>
    <el-form :model="form" label-position="top">
      <el-form-item label="Image URLs (one per line)">
        <el-input v-model="form.urls" type="textarea" :rows="5" placeholder="https://..." />
      </el-form-item>
      <el-form-item label="Tags">
        <div style="display: flex; flex-direction: column; width: 100%; gap: 10px;">
          <el-select
            v-model="form.tags"
            multiple
            filterable
            placeholder="Select existing tags"
            style="width: 100%;"
          >
            <el-option v-for="tag in allTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
          <div style="display: flex;">
            <el-input
              v-model="newTagInput"
              placeholder="Add new tags (comma-separated)"
              style="flex-grow: 1; margin-right: 10px;"
              @keyup.enter="addNewTags"
            />
            <el-button @click="addNewTags">Add</el-button>
          </div>
        </div>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit" style="width: 100%;">Create</el-button>
      </el-form-item>
    </el-form>
  </el-card>
</template>

<script setup>
import { ref, reactive, defineEmits, defineProps } from 'vue';
import { addBulkImages } from '../services/api';
import { ElMessage } from 'element-plus';

const props = defineProps({
  allTags: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['tags-updated']);

const form = reactive({
  urls: '',
  tags: [],
});
const newTagInput = ref('');

const onSubmit = async () => {
  const urls = form.urls.split('\n').map(url => url.trim()).filter(url => url);
  if (urls.length === 0) {
    ElMessage.error('At least one Image URL is required.');
    return;
  }
  
  try {
    await addBulkImages({
      urls: urls,
      tags: form.tags,
    });
    ElMessage.success(`${urls.length} image(s) added successfully!`);
    emit('tags-updated');
    form.urls = '';
    form.tags = [];
    newTagInput.value = '';
  } catch (error) {
    console.error('Failed to add images:', error);
    ElMessage.error('Failed to add images.');
  }
};

const addNewTags = () => {
  if (!newTagInput.value) return;
  const newTags = newTagInput.value.split(',').map(t => t.trim()).filter(t => t);
  const uniqueNewTags = newTags.filter(t => !form.tags.includes(t));
  form.tags.push(...uniqueNewTags);
  newTagInput.value = '';
};
</script>

<style scoped>
.uploader-card {
  margin-bottom: 2rem;
}
.card-header {
  font-weight: 600;
  color: #1f2937;
}
</style>