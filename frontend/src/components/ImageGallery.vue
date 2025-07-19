<template>
  <div>
    <!-- Controls -->
    <el-card class="controls-card">
      <el-row :gutter="20" align="middle">
        <el-col :span="10">
          <el-input
            v-model="filters.filename"
            placeholder="Search by filename..."
            clearable
            prefix-icon="el-icon-search"
          />
        </el-col>
        <el-col :span="10">
          <el-select
            v-model="filters.tags"
            multiple
            filterable
            placeholder="Filter by tags"
            style="width: 100%"
          >
            <el-option v-for="tag in allTags" :key="tag" :label="tag" :value="tag" />
          </el-select>
        </el-col>
        <el-col :span="8" style="display: flex; align-items: center; gap: 10px;">
          <el-checkbox
            v-if="images.length > 0"
            :model-value="isAllSelected"
            @change="handleSelectAll"
            :indeterminate="isIndeterminate"
          >
            Select All
          </el-checkbox>
          <el-dropdown @command="handleBulkCommand" v-if="selectedImages.length > 0">
            <el-button type="primary">
              Actions ({{ selectedImages.length }})<i class="el-icon-arrow-down el-icon--right"></i>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="addTags">Add Tags</el-dropdown-item>
                <el-dropdown-item command="delete" divided>Delete Selected</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </el-col>
      </el-row>
    </el-card>

    <!-- Image Grid -->
    <transition-group name="image-list" tag="div" class="image-grid">
      <el-card v-for="(image, index) in images" :key="image.id" class="image-card" shadow="hover">
        <el-checkbox
          :model-value="selectedImages.includes(image.id)"
          @change="toggleImageSelection(image.id)"
          class="card-checkbox"
        ></el-checkbox>
        <div class="image-preview-wrapper">
          <el-image
            :src="image.url"
            :preview-src-list="images.map(i => i.url)"
            :initial-index="index"
            fit="cover"
            class="image-preview"
            lazy
            :preview-teleported="true"
          />
          <div class="actions-overlay">
            <el-tooltip content="Copy Link" placement="top">
              <el-button circle type="primary" icon="el-icon-link" @click.stop="copyToClipboard(image.url, $event)" />
            </el-tooltip>
            <el-tooltip content="Rename" placement="top">
              <el-button circle type="info" icon="el-icon-edit-outline" @click.stop="openRenameDialog(image)" />
            </el-tooltip>
            <el-tooltip content="Edit Tags" placement="top">
              <el-button circle type="warning" icon="el-icon-edit" @click.stop="openEditDialog(image)" />
            </el-tooltip>
            <el-tooltip content="Delete" placement="top">
              <el-button circle type="danger" icon="el-icon-delete" @click.stop="handleDelete(image.id)" />
            </el-tooltip>
          </div>
        </div>
        <div class="info-section">
          <span class="filename" :title="image.filename">{{ image.filename }}</span>
          <span class="date">{{ new Date(image.created_at).toLocaleDateString() }}</span>
          <div class="tags-section">
            <el-tag
              v-for="tag in image.tags"
              :key="tag.id"
              size="small"
              :type="tag.name.toLowerCase() === 'r18' ? 'danger' : 'success'"
            >
              {{ tag.name }}
            </el-tag>
          </div>
        </div>
      </el-card>
    </transition-group>

    <!-- Pagination -->
    <el-pagination
      v-if="pagination.total > 0"
      v-model:current-page="pagination.page"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      :page-sizes="[10, 20, 50, 100]"
      layout="total, sizes, prev, pager, next"
      @current-change="handlePageChange"
      @size-change="handleSizeChange"
      class="pagination"
    />
  </div>

  <!-- Rename Dialog -->
  <el-dialog v-model="renameDialogVisible" title="Rename Image" width="400px">
    <el-input v-model="newFilename" placeholder="Enter new filename"></el-input>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="renameDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleRename">Confirm</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- Edit Dialog -->
  <el-dialog v-model="editDialogVisible" title="Edit Tags" width="400px">
    <div class="selected-tags-preview">
      <el-tag
        v-for="tag in currentImageTags"
        :key="tag"
        closable
        @close="handleRemoveTag(tag)"
        :type="tag.toLowerCase() === 'r18' ? 'danger' : 'success'"
        style="margin: 2px;"
      >
        {{ tag }}
      </el-tag>
    </div>
    <el-divider />
    <div style="display: flex; flex-direction: column; gap: 10px;">
      <el-select
        v-model="tagsToAdd"
        multiple
        filterable
        placeholder="Select existing tags to add"
        style="width: 100%;"
        @change="addSelectedTagsToDialog"
      >
        <el-option v-for="tag in availableTags" :key="tag" :label="tag" :value="tag" />
      </el-select>
      <div style="display: flex;">
        <el-input
          v-model="newTagInput"
          placeholder="Or add new tags (comma-separated)"
          style="flex-grow: 1; margin-right: 10px;"
          @keyup.enter="addNewTagsToDialog"
        />
        <el-button @click="addNewTagsToDialog">Add</el-button>
      </div>
    </div>
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="editDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleUpdateTags">Confirm</el-button>
      </span>
    </template>
  </el-dialog>

  <!-- Bulk Add Tags Dialog -->
  <el-dialog v-model="bulkAddTagsDialogVisible" title="Bulk Add Tags">
    <el-input
      v-model="bulkTagsInput"
      placeholder="Enter new tags, separated by commas"
    />
    <template #footer>
      <span class="dialog-footer">
        <el-button @click="bulkAddTagsDialogVisible = false">Cancel</el-button>
        <el-button type="primary" @click="handleBulkAddTags">Confirm</el-button>
      </span>
    </template>
  </el-dialog>
</template>

<script setup>
import { ref, reactive, onMounted, watch, defineExpose, defineEmits, defineProps, computed } from 'vue';
import { getImages, deleteImage, updateImageTags, deleteImagesBulk, addTagsToImagesBulk, renameImage } from '../services/api';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Search, Link, Edit, Delete } from '@element-plus/icons-vue';
import ClipboardJS from 'clipboard';

const props = defineProps({
  allTags: {
    type: Array,
    default: () => []
  }
});

const emit = defineEmits(['tags-updated']);

const images = ref([]);
const renameDialogVisible = ref(false);
const newFilename = ref('');
const editDialogVisible = ref(false);
const currentImage = ref(null);
const currentImageTags = ref([]);
const newTagInput = ref('');
const tagsToAdd = ref([]);
const selectedImages = ref([]);
const bulkAddTagsDialogVisible = ref(false);
const bulkTags = ref([]);
const bulkTagsInput = ref('');

const pagination = reactive({
  page: 1,
  pageSize: 10,
  total: 0,
});

const filters = reactive({
  filename: '',
  tags: [],
});

const availableTags = computed(() => {
  return props.allTags.filter(tag => !currentImageTags.value.includes(tag));
});

const fetchImages = async () => {
  try {
    const params = {
      skip: (pagination.page - 1) * pagination.pageSize,
      limit: pagination.pageSize,
      sort_by: 'created_at',
      sort_order: 'desc',
      tags: filters.tags.join(',') || null,
      filename_like: filters.filename || null,
    };
    const data = await getImages(params);
    images.value = data.images;
    pagination.total = data.total;
  } catch (error) {
    console.error('Failed to fetch images:', error);
    ElMessage.error('Failed to fetch images.');
  }
};

const isAllSelected = computed(() => {
  if (images.value.length === 0) return false;
  return selectedImages.value.length === images.value.length;
});

const isIndeterminate = computed(() => {
  return selectedImages.value.length > 0 && !isAllSelected.value;
});


watch(filters, fetchImages, { deep: true });


const handlePageChange = (page) => {
  pagination.page = page;
  fetchImages();
};

const handleSizeChange = (size) => {
  pagination.pageSize = size;
  fetchImages();
};

const handleDelete = (id) => {
  ElMessageBox.confirm('This will permanently delete the image. Continue?', 'Warning', {
    confirmButtonText: 'OK',
    cancelButtonText: 'Cancel',
    type: 'warning',
  }).then(async () => {
    try {
      await deleteImage(id);
      ElMessage.success('Image deleted successfully!');
      fetchImages();
      emit('tags-updated');
    } catch (error) {
      console.error('Failed to delete image:', error);
      ElMessage.error('Failed to delete image.');
    }
  });
};

const openRenameDialog = (image) => {
  currentImage.value = image;
  newFilename.value = image.filename;
  renameDialogVisible.value = true;
};

const handleRename = async () => {
  if (!currentImage.value || !newFilename.value) return;
  try {
    await renameImage(currentImage.value.id, newFilename.value);
    ElMessage.success('Image renamed successfully!');
    renameDialogVisible.value = false;
    fetchImages();
  } catch (error) {
    console.error('Failed to rename image:', error);
    ElMessage.error('Failed to rename image.');
  }
};

const openEditDialog = (image) => {
  currentImage.value = image;
  currentImageTags.value = image.tags.map(tag => tag.name);
  newTagInput.value = '';
  tagsToAdd.value = [];
  editDialogVisible.value = true;
};

const handleUpdateTags = async () => {
  if (!currentImage.value) return;
  try {
    await updateImageTags(currentImage.value.id, currentImageTags.value);
    ElMessage.success('Tags updated successfully!');
    editDialogVisible.value = false;
    fetchImages();
    emit('tags-updated');
  } catch (error) {
    console.error('Failed to update tags:', error);
    ElMessage.error('Failed to update tags.');
  }
};

const addNewTagsToDialog = () => {
  if (!newTagInput.value) return;
  const newTags = newTagInput.value.split(',').map(t => t.trim()).filter(t => t);
  const uniqueNewTags = newTags.filter(t => !currentImageTags.value.includes(t));
  currentImageTags.value.push(...uniqueNewTags);
  newTagInput.value = '';
};

const handleRemoveTag = (tagToRemove) => {
  currentImageTags.value = currentImageTags.value.filter(tag => tag !== tagToRemove);
};

const addSelectedTagsToDialog = (selected) => {
  if (!selected || selected.length === 0) return;
  const newTags = selected.filter(t => !currentImageTags.value.includes(t));
  currentImageTags.value.push(...newTags);
  tagsToAdd.value = [];
};

const handleSelectAll = (value) => {
  if (value) {
    selectedImages.value = images.value.map(img => img.id);
  } else {
    selectedImages.value = [];
  }
};

const toggleImageSelection = (id) => {
  const index = selectedImages.value.indexOf(id);
  if (index > -1) {
    selectedImages.value.splice(index, 1);
  } else {
    selectedImages.value.push(id);
  }
};

const handleBulkCommand = (command) => {
  if (command === 'addTags') {
    bulkTagsInput.value = '';
    bulkAddTagsDialogVisible.value = true;
  } else if (command === 'delete') {
    ElMessageBox.confirm(`This will permanently delete ${selectedImages.value.length} images. Continue?`, 'Warning', {
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }).then(async () => {
      try {
        await deleteImagesBulk(selectedImages.value);
        ElMessage.success('Bulk delete successful!');
        selectedImages.value = [];
        fetchImages();
        emit('tags-updated');
      } catch (error) {
        console.error('Failed to bulk delete images:', error);
        ElMessage.error('Failed to bulk delete images.');
      }
    });
  }
};

const handleBulkAddTags = async () => {
  const tags = bulkTagsInput.value.split(',').map(t => t.trim()).filter(t => t);
  if (tags.length === 0) {
    ElMessage.error('Please enter at least one tag.');
    return;
  }
  try {
    await addTagsToImagesBulk(selectedImages.value, tags);
    ElMessage.success('Tags added to selected images successfully!');
    bulkAddTagsDialogVisible.value = false;
    selectedImages.value = [];
    fetchImages();
    emit('tags-updated');
  } catch (error) {
    console.error('Failed to bulk add tags:', error);
    ElMessage.error('Failed to bulk add tags.');
  }
};

const copyToClipboard = (text, event) => {
  const clipboard = new ClipboardJS(event.currentTarget, {
    text: () => text
  });

  clipboard.on('success', (e) => {
    ElMessage.success('Copied to clipboard!');
    e.clearSelection();
    clipboard.destroy();
  });

  clipboard.on('error', (e) => {
    ElMessage.error('Failed to copy!');
    console.error('Action:', e.action);
    console.error('Trigger:', e.trigger);
    clipboard.destroy();
  });

  // Manually trigger the copy action
  clipboard.onClick(event);
};

onMounted(fetchImages);

</script>

<style scoped>
.controls-card {
  margin-bottom: 2rem;
}

.image-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
}

.image-card {
  position: relative;
  transition: all 0.3s ease;
}

.card-checkbox {
  position: absolute;
  top: 10px;
  left: 10px;
  z-index: 10;
}

.image-preview-wrapper {
  position: relative;
  aspect-ratio: 16 / 10;
  overflow: hidden;
}

.image-preview {
  width: 100%;
  height: 100%;
  object-fit: cover;
  transition: transform 0.3s ease;
}

.image-card:hover .image-preview {
  transform: scale(1.05);
}

.actions-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 10px;
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none; /* Overlay itself doesn't capture clicks */
}

.actions-overlay > * {
  pointer-events: auto; /* But its children (buttons) do */
}

.image-card:hover .actions-overlay {
  opacity: 1;
}

.info-section {
  padding: 14px;
}

.filename {
  font-weight: 600;
  color: #1f2937;
  display: block;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.date {
  font-size: 0.8rem;
  color: #6b7280;
  margin-bottom: 10px;
  display: block;
}

.tags-section {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
}

.pagination {
  margin-top: 2rem;
  justify-content: center;
}

.selected-tags-preview {
  margin-bottom: 10px;
}

/* Transition Group animations */
.image-list-move,
.image-list-enter-active,
.image-list-leave-active {
  transition: all 0.5s ease;
}
.image-list-enter-from,
.image-list-leave-to {
  opacity: 0;
  transform: translateY(30px);
}
.image-list-leave-active {
  position: absolute;
}
</style>