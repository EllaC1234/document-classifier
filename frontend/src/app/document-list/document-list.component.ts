import { Component, OnInit } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';

type PreviousDoc = {
  filename: string;
  category: string;
  confidence: number;
  upload_time: string;
}

@Component({
  selector: 'document-list',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './document-list.component.html',
  styleUrl: './document-list.component.css'
})
export class DocumentListComponent implements OnInit {
  data: PreviousDoc[] = [];
  loading: boolean = true;
  readonly API_URL = 'http://127.0.0.1:8000/api/get_documents';

  tableHeaders = [
    { label: 'Filename', class: 'col-md-4' },
    { label: 'Predicted Category', class: 'col-md-3' },
    { label: 'Confidence', class: 'col-md-3' },
    { label: 'Upload Time', class: 'col-md-2' }
  ];

  constructor(private http: HttpClient) { }

  ngOnInit(): void {
    this.fetchData();
  }

  fetchData() {
    this.loading = true;

    this.http.get<PreviousDoc[]>(this.API_URL).subscribe({
      next: (data) => {
        this.data = data.reverse();
        this.loading = false;
      },
      error: (error) => {
        console.error('Error fetching data:', error);
        this.loading = false;
      }
    });
  }
}
