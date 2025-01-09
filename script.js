document.addEventListener('DOMContentLoaded', () => {
    const dropZone = document.getElementById('dropZone');
    const fileInput = document.getElementById('fileInput');
    const resultMessage = document.getElementById('resultMessage');
    const resultImage = document.getElementById('resultImage');
    const resultTransparent = document.getElementById('resultTransparent');

    // �����ק���򴥷��ļ�ѡ��
    dropZone.addEventListener('click', () => {
        fileInput.click();
    });

    // ��ק�ļ�����ק����
    dropZone.addEventListener('dragover', (e) => {
        e.preventDefault();
        dropZone.classList.add('hover');
    });

    dropZone.addEventListener('dragleave', () => {
        dropZone.classList.remove('hover');
    });

    dropZone.addEventListener('drop', (e) => {
        e.preventDefault();
        dropZone.classList.remove('hover');
        const files = e.dataTransfer.files;
        if (files.length) {
            uploadImage(files[0]);
        }
    });

    // �ļ�ѡ������仯
    fileInput.addEventListener('change', (e) => {
        const files = e.target.files;
        if (files.length) {
            uploadImage(files[0]);
        }
    });

    // �ϴ�ͼƬ�����÷ָ��͸���������� API
    async function uploadImage(file) {
        resultMessage.textContent = 'Processing image, please wait...';
        resultImage.innerHTML = '';
        resultTransparent.innerHTML = '';

        const formData = new FormData();
        formData.append('image', file);

        try {
            // ����ʵ���ָ� API
            const segmentationResponse = await fetch('/process_image', {
                method: 'POST',
                body: formData,
            });

            const segmentationResult = await segmentationResponse.json();
            if (segmentationResult.success) {
                resultMessage.textContent = 'Segmentation completed!';
                segmentationResult.files.forEach((file) => {
                    const img = document.createElement('img');
                    img.src = file;
                    resultImage.appendChild(img);
                });
            } else {
                resultMessage.textContent = `Segmentation error: ${segmentationResult.message}`;
            }
        } catch (error) {
            resultMessage.textContent = 'Error during segmentation processing.';
            console.error(error);
        }

        try {
            // ����͸������ʵ������ API
            const transparentResponse = await fetch('/process_image_with_masks', {
                method: 'POST',
                body: formData,
            });

            const transparentResult = await transparentResponse.json();
            if (transparentResult.success) {
                resultMessage.textContent += ' Transparent processing completed!';
                const fullTransparentImg = document.createElement('img');
                fullTransparentImg.src = transparentResult.transparent_full;
                resultTransparent.appendChild(fullTransparentImg);

                transparentResult.instances.forEach((file) => {
                    const img = document.createElement('img');
                    img.src = file;
                    resultTransparent.appendChild(img);
                });
            } else {
                resultMessage.textContent += ` Transparent processing error: ${transparentResult.message}`;
            }
        } catch (error) {
            resultMessage.textContent += ' Error during transparent background processing.';
            console.error(error);
        }
    }
});
