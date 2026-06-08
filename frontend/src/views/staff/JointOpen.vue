<template>
  <div>
    <PageHeader title="联合开户" />

    <PagePanel width="narrow">
      <PageInfoCard title="办理说明" style="margin-bottom: 24px;">
        <p class="inline-tip">
          本页录入自然人客户资料并提交联合开户申请。审批通过时由审批人员设置银行卡号、交易密码和取款密码，
          系统随后连续创建证券账户、资金账户并建立一对一有效绑定。
        </p>
      </PageInfoCard>

      <PageFormBlock>
        <el-form
          ref="formRef"
          :model="form"
          :rules="rules"
          class="page-form-stack"
          @submit.prevent
        >
          <el-form-item label="投资者姓名" label-position="top" prop="investorName" style="margin-bottom: 0;">
            <el-input v-model="form.investorName" placeholder="请输入姓名" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="证件类型" label-position="top" prop="idType" style="margin-bottom: 0;">
            <el-select v-model="form.idType" placeholder="请选择" style="width: 100%;">
              <el-option
                v-for="(label, key) in IdTypeLabel"
                :key="key"
                :label="label"
                :value="key"
              />
            </el-select>
          </el-form-item>
          <el-form-item label="证件号码" label-position="top" prop="idNo" style="margin-bottom: 0;">
            <el-input v-model="form.idNo" placeholder="请输入证件号码" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="联系电话" label-position="top" prop="phone" style="margin-bottom: 0;">
            <el-input v-model="form.phone" placeholder="请输入手机号" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="性别" label-position="top" prop="gender" style="margin-bottom: 0;">
            <el-select v-model="form.gender" placeholder="请选择性别" style="width: 100%;">
              <el-option label="男" value="男" />
              <el-option label="女" value="女" />
            </el-select>
          </el-form-item>
          <el-form-item label="联系地址" label-position="top" prop="address" style="margin-bottom: 0;">
            <el-input v-model="form.address" placeholder="请输入开户地址或常住地址" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="职业" label-position="top" prop="occupation" style="margin-bottom: 0;">
            <el-input v-model="form.occupation" placeholder="请输入职业" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="学历" label-position="top" prop="educationLevel" style="margin-bottom: 0;">
            <el-select v-model="form.educationLevel" placeholder="请选择学历" style="width: 100%;">
              <el-option label="高中及以下" value="高中及以下" />
              <el-option label="大专" value="大专" />
              <el-option label="本科" value="本科" />
              <el-option label="硕士" value="硕士" />
              <el-option label="博士及以上" value="博士及以上" />
            </el-select>
          </el-form-item>
          <el-form-item label="工作单位" label-position="top" prop="employer" style="margin-bottom: 0;">
            <el-input v-model="form.employer" placeholder="请输入工作单位" style="width: 100%;" />
          </el-form-item>
          <el-form-item label="代办人证件号" label-position="top" prop="agentIdNumber" style="margin-bottom: 0;">
            <el-input
              v-model="form.agentIdNumber"
              placeholder="如为代办开户请填写，否则可留空"
              style="width: 100%;"
            />
          </el-form-item>
          <el-form-item label="申请备注" label-position="top" prop="remark" style="margin-bottom: 0;">
            <el-input
              v-model="form.remark"
              type="textarea"
              :rows="3"
              maxlength="1000"
              show-word-limit
              placeholder="可填写开户申请备注"
              style="width: 100%;"
            />
          </el-form-item>
        </el-form>

        <PageActionRow
          primary-text="提交联合开户申请"
          secondary-text="重置"
          :primary-disabled="loading"
          @primary="submitJoint"
          @secondary="resetForm"
        />
      </PageFormBlock>
    </PagePanel>
  </div>
</template>

<script setup>
import { reactive, ref } from 'vue'
import { ElMessage } from 'element-plus'
import { submitOpenApplication } from '@/utils/request'
import { IdTypeLabel } from '@/constants/enums'
import PageActionRow from '@/components/PageActionRow.vue'
import PageFormBlock from '@/components/PageFormBlock.vue'
import PageHeader from '@/components/PageHeader.vue'
import PageInfoCard from '@/components/PageInfoCard.vue'
import PagePanel from '@/components/PagePanel.vue'

const buildInitialForm = () => ({
  investorName: '',
  idType: 'ID_CARD',
  idNo: '',
  phone: '',
  gender: '',
  address: '',
  occupation: '',
  educationLevel: '',
  employer: '',
  agentIdNumber: '',
  remark: '联合开户申请'
})

const form = reactive(buildInitialForm())
const formRef = ref(null)
const loading = ref(false)

const rules = {
  investorName: [{ required: true, message: '请输入姓名', trigger: 'blur' }],
  idType: [{ required: true, message: '请选择证件类型', trigger: 'change' }],
  idNo: [{ required: true, message: '请输入证件号码', trigger: 'blur' }],
  phone: [{ required: true, message: '请输入联系电话', trigger: 'blur' }],
  gender: [{ required: true, message: '请选择性别', trigger: 'change' }],
  address: [{ required: true, message: '请输入联系地址', trigger: 'blur' }],
  occupation: [{ required: true, message: '请输入职业', trigger: 'blur' }],
  educationLevel: [{ required: true, message: '请选择学历', trigger: 'change' }],
  employer: [{ required: true, message: '请输入工作单位', trigger: 'blur' }]
}

const submitJoint = async () => {
  await formRef.value.validate()
  loading.value = true
  try {
    const res = await submitOpenApplication({
      investorName: form.investorName.trim(),
      idType: form.idType,
      idNo: form.idNo.trim(),
      phone: form.phone.trim(),
      gender: form.gender,
      address: form.address.trim(),
      occupation: form.occupation.trim(),
      educationLevel: form.educationLevel,
      employer: form.employer.trim(),
      agentIdNumber: form.agentIdNumber.trim(),
      remark: form.remark.trim() || '联合开户申请'
    })
    ElMessage.success(`联合开户申请已提交，申请编号：${res.data.applicationId}`)
    resetForm()
  } catch (error) {
    ElMessage.error(error.message || '开户申请提交失败')
  } finally {
    loading.value = false
  }
}

const resetForm = () => {
  Object.assign(form, buildInitialForm())
  formRef.value?.resetFields()
}
</script>

<style scoped>
.page-form-stack {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.inline-tip {
  margin: 0;
  line-height: 1.7;
  color: var(--color-text-muted);
}
</style>
