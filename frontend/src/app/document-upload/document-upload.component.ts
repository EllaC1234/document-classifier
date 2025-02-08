import { Component } from '@angular/core';
import { FileUploader } from 'ng2-file-upload';
import { FileUploadModule } from 'ng2-file-upload';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'document-upload',
  imports: [
    CommonModule,
    FileUploadModule
  ],
  templateUrl: './document-upload.component.html',
  styleUrl: './document-upload.component.css',
  standalone: true
})

export class DocumentUploadComponent {
  URL = 'http://127.0.0.1:8000/upload';
  uploader: FileUploader;
  hasBaseDropZoneOver: boolean = false;
  uploadMessage: string = '';

  constructor() {
    this.uploader = new FileUploader({
      url: this.URL,
      itemAlias: 'file',
      removeAfterUpload: true,
      autoUpload: false
    });

    this.uploader.onCompleteItem = (item: any, response: any, status: any) => {
      try {
        const result = JSON.parse(response);
        console.log('File upload details:', {
          'Filename': result.filename,
          'Category': result.category,
          'Upload Time': result.upload_time,
          'Confidence Scores': result.confidence_scores
        });
        this.uploadMessage = `Upload complete! Document classified as: ${result.category}`;
      } catch (error) {
        console.error('Error parsing response:', error);
        this.uploadMessage = 'Upload complete, but error parsing response';
      }
    };

    this.uploader.onErrorItem = (item: any, response: any, status: any) => {
      console.error('File upload failed:', response);
      this.uploadMessage = 'Upload failed: ' + response;
    };

    this.uploader.onProgressItem = (fileItem: any, progress: any) => {
      console.log('File ' + fileItem.file.name + ' progress: ' + progress + '%');
    };

    this.uploader.onAfterAddingFile = (fileItem: any) => {
      this.uploadMessage = '';
    };
  }

  public fileOverBase(e: any): void {
    this.hasBaseDropZoneOver = e;
  }

  uploadAll() {
    this.uploadMessage = "Uploading..."
    this.uploader.uploadAll();
  }
}
