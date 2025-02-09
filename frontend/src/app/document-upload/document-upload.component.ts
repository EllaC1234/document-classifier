import { Component } from '@angular/core';
import { FileUploader } from 'ng2-file-upload';
import { FileUploadModule } from 'ng2-file-upload';
import { CommonModule } from '@angular/common';

interface Prediction {
  category: string;
  confidence: number;
}

interface ClassificationResponse {
  fileName: string;
  predictions: Prediction[];
}

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
  classificationResults: ClassificationResponse | null = null;

  constructor() {
    this.uploader = new FileUploader({
      url: this.URL,
      itemAlias: 'file',
      removeAfterUpload: false,
      autoUpload: false
    });

    // Clear previous file when new file is added
    this.uploader.onAfterAddingFile = (fileItem: any) => {
      if (this.uploader.queue.length > 1) {
        this.uploader.queue[0].remove();
      }
      this.uploadMessage = '';
    };

    this.uploader.onCompleteItem = (item: any, response: any, status: any) => {
      try {
        const result = JSON.parse(response);
        console.log('Raw API response: ', result);
        this.classificationResults = {
          fileName: item.file.name,
          predictions: result.predictions
        };
        console.log('Processed results: ', this.classificationResults);
        this.uploadMessage = '';
        item.remove();
      } catch (error) {
        this.uploadMessage = 'Upload complete, but error parsing response';
      }
    };

    this.uploader.onErrorItem = (item: any, response: any, status: any) => {
      this.uploadMessage = 'Upload failed: ' + response;
    };
  }

  public fileOverBase(e: any): void {
    this.hasBaseDropZoneOver = e;
  }

  uploadAll() {
    this.uploader.uploadAll();
  }
}
