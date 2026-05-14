// src/lib/cloudinary.ts
const CLOUD_NAME = process.env.NEXT_PUBLIC_CLOUDINARY_CLOUD_NAME;
const UPLOAD_PRESET = process.env.NEXT_PUBLIC_CLOUDINARY_UPLOAD_PRESET;

if (!CLOUD_NAME || !UPLOAD_PRESET) {
  // Chỉ log ở runtime client, để dễ debug
  console.warn("⚠️ Thiếu Cloudinary env: NEXT_PUBLIC_CLOUDINARY_*");
}

export async function uploadToCloudinary(file: File): Promise<string> {
  if (!CLOUD_NAME || !UPLOAD_PRESET) {
    throw new Error("Cloudinary chưa được cấu hình đúng .env.local");
  }

  const formData = new FormData();
  formData.append("file", file);
  formData.append("upload_preset", UPLOAD_PRESET);

  const res = await fetch(`https://api.cloudinary.com/v1_1/${CLOUD_NAME}/upload`, {
    method: "POST",
    body: formData,
  });

  if (!res.ok) {
    throw new Error("Upload Cloudinary thất bại");
  }

  const data = await res.json();
  // data.secure_url là URL của ảnh
  return data.secure_url as string;
}
