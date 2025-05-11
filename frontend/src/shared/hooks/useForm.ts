import { useState, ChangeEvent, FormEvent } from 'react';

interface UseFormProps<T> {
  initialValues: T;
  onSubmit: (values: T) => void | Promise<void>;
  validate?: (values: T) => Partial<Record<keyof T, string>>;
}

/**
 * 表单处理 Hook
 * @param initialValues 初始值
 * @param onSubmit 提交回调
 * @param validate 验证函数
 * @returns 表单状态和处理函数
 */
const useForm = <T extends Record<string, any>>({
  initialValues,
  onSubmit,
  validate,
}: UseFormProps<T>) => {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Partial<Record<keyof T, string>>>({});
  const [isSubmitting, setIsSubmitting] = useState(false);

  // 处理输入变化
  const handleChange = (
    e: ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>
  ) => {
    const { name, value, type } = e.target as HTMLInputElement;
    
    // 处理复选框
    if (type === 'checkbox') {
      const { checked } = e.target as HTMLInputElement;
      setValues({
        ...values,
        [name]: checked,
      });
      return;
    }
    
    // 处理其他输入
    setValues({
      ...values,
      [name]: value,
    });
    
    // 清除错误
    if (errors[name as keyof T]) {
      setErrors({
        ...errors,
        [name]: undefined,
      });
    }
  };

  // 处理表单提交
  const handleSubmit = async (e: FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    
    // 验证表单
    if (validate) {
      const validationErrors = validate(values);
      const hasErrors = Object.keys(validationErrors).length > 0;
      
      if (hasErrors) {
        setErrors(validationErrors);
        return;
      }
    }
    
    // 提交表单
    setIsSubmitting(true);
    try {
      await onSubmit(values);
    } finally {
      setIsSubmitting(false);
    }
  };

  // 重置表单
  const resetForm = () => {
    setValues(initialValues);
    setErrors({});
  };

  // 设置字段值
  const setFieldValue = (name: keyof T, value: any) => {
    setValues({
      ...values,
      [name]: value,
    });
    
    // 清除错误
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: undefined,
      });
    }
  };

  return {
    values,
    errors,
    isSubmitting,
    handleChange,
    handleSubmit,
    resetForm,
    setFieldValue,
  };
};

export default useForm;
