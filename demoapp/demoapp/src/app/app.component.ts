import { Component, Renderer2, ElementRef } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { throwError, tap, catchError } from 'rxjs';
import { NotifierService } from 'angular-notifier';
import { ToastrService } from 'ngx-toastr';
import { ContentManagementComponent } from './content-management/content-management.component';

let headers = new HttpHeaders({
  'ngrok-skip-browser-warning': '6024',
  'Content-Type': 'application/json'
});


@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.css'],
  template:
    '<notifier-container></notifier-container>'
  ,
})
export class AppComponent {

  isLoading = false;
  sliderValue = 0.65;
  searchText: string | null = null;
  data: any;
  private notifier: NotifierService;
  public constructor(private http: HttpClient,
    private renderer: Renderer2,
    private el: ElementRef,
    private toastr: ToastrService,

    notifierService: NotifierService) { this.notifier = notifierService; }
  title = 'Smart Search';
  selectedFiles: FileList | null = null;
  imageUrls: string[] = [];
  uploadMessage: string | null = null;
  chatMessages: string[] = [];
  userMessage: string = '';
  titles = 'chatbot';
  chatVisible = false;
  images: Array<{
    name: string;
    image: string;
  }> = [];
  message = null

/**
 * Show a notification.
 * @param {string} type - The type of the notification.
 * @param {string} message - The message to be displayed in the notification.
 */
public showNotification(type: string, message: string): void {
  this.notifier.notify(type, message);
}

/**
 * Event handler for file selection.
 * @param {any} event - The event object.
 */
onFileSelected(event: any) {
  this.selectedFiles = event.target.files;
  this.uploadFiles();
}

/**
 * Open the file selection dialog.
 */
openFileSelection() {
  const fileInput = document.getElementById('fileInput');
  if (fileInput) {
    fileInput.click();
  }
}

/**
 * Upload the selected files.
 */
uploadFiles() {
  this.imageUrls = [];
  this.isLoading = true;
  this.uploadMessage = '';

  if (this.selectedFiles && this.selectedFiles.length > 0) {
    const promises = [];

    for (let i = 0; i < this.selectedFiles.length; i++) {
      const file = this.selectedFiles.item(i);

      if (file) {
        const filename = file.name;
        const reader = new FileReader();

        // Create a new promise for each file read operation
        const promise = new Promise((resolve, reject) => {
          reader.onload = (e) => {
            const base64Image = (e.target as FileReader).result as string;

            const image = {
              name: filename,
              image: base64Image
            };

            this.images.push(image);
            resolve(null);
          };

          reader.onerror = (e) => {
            reject(e);
          };

          reader.readAsDataURL(file);
        });

        promises.push(promise);
      }
    }

    // Wait for all promises to resolve
    Promise.all(promises).then(() => {
      // Convert the images array to a JSON string
      const imagesJSON = JSON.stringify(this.images);

      // Send the JSON string to the backend
      this.http.post('http://127.0.0.1:8000/upload/', { images: imagesJSON })
        .subscribe(
          response => {
            // Process successful upload
            console.log('Upload successful!');
            this.isLoading = false;
            this.uploadMessage = 'Upload successful!';
            this.showNotification('success', this.uploadMessage);

            // Clear the images array after successful upload
            this.images = [];

            // Update the image URLs
            this.updateImageUrls(response);
          },
          error => {
            // Handle upload error
            console.error('Upload failed!');
            this.isLoading = false;
            this.uploadMessage = 'Upload failed!';
            this.showNotification('error', this.uploadMessage);
            return throwError(() => error);
          }
        );
    }).catch((error) => {
      console.error('Error reading files:', error);
    });
  } else {
    console.log('No files selected.');
  }
}


/**
 * Update the image URLs based on the server response.
 * @param {any} response - The server response.
 */
updateImageUrls(response: any) {
  if (response.imageUrls) {
    this.imageUrls = response.imageUrls;
  }
}

/**
 * Angular lifecycle hook that is called after data-bound properties of a directive are initialized.
 */
ngOnInit() {
}

/**
 * Event handler for the Enter key press.
 * @param {any} event - The event object.
 */
onEnter(event: any) {
  if (event.keyCode === 13) {
    this.onSearch();
  }
}

/**
 * Perform a search operation.
 */
async onSearch() {
  // Set loading state and clear any previous messages
  this.isLoading = true;
  this.uploadMessage = '';

  // Define headers for the fetch request
  const headers = {
    'Content-Type': 'application/json'
  };

  // Create an AbortController instance to allow aborting the fetch request
  const controller = new AbortController();

  // Set a timeout to abort the request if it takes too long
  const timeout = setTimeout(() => {
    controller.abort();
  }, 10000);

  try {
    // Make the fetch request
    const response = await fetch(`http://127.0.0.1:8000/api/search?query=${this.searchText}&sliderValue=${this.sliderValue}`, {
      method: 'GET',
      mode: 'cors',
      credentials: 'same-origin',
      headers: headers,
      signal: controller.signal  // Pass the abort signal
    });

    // Check if the response was successful
    if (!response.ok) {
      console.log('HTTP status:', response.status);

      // Check the content type of the response
      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        // If it's JSON, parse it and log the details
        const errorDetails = await response.json();
        console.error('Server error details:', errorDetails);
      } else {
        // If it's not JSON, just log the text
        const errorText = await response.text();
        console.error('Server error text:', errorText);
      }

      // Throw an error to be caught in the catch block
      throw new Error('Network response was not ok');
    }

    // Parse the response as JSON
    const result = await response.json();
    console.log(result);

    // Update the state and show a success notification
    this.isLoading = false;
    this.uploadMessage = 'Search successful!';
    this.showNotification('success', this.uploadMessage);

    // Store the result data
    this.data = result;
  } catch (error) {
    // Log any errors and update the state
    console.error('There has been a problem with your fetch operation:', error);
    this.isLoading = false;
    this.uploadMessage = 'Search error!';
    this.showNotification('error', this.uploadMessage);
  } finally {
    // Clear the timeout regardless of whether the fetch was successful
    clearTimeout(timeout);
  }
}


  // sendMessage() {
  //   if (this.userMessage.trim() === '') return;
  //   this.chatMessages.push(`you: ${this.userMessage}`);

  //   const userMessage = this.userMessage;

  //   // Gửi yêu cầu đến phía backend bằng HttpClient
  //   this.http.post('http://103.176.147.70:8512/api/chatbot/', {user_message: userMessage})
  //     .subscribe((response: any) => {
  //       if (response && response.response) {
  //         this.chatMessages.push(`Chatbot: ${response.response}`); // Hiển thị câu trả lời từ phía backend (chatbot)
  //       } else {
  //         console.error('Lỗi khi nhận câu trả lời từ phía backend.');
  //       }
  //     }, (error) => {
  //       console.error('Lỗi khi gửi yêu cầu đến phía backend:', error);
  //     });

  //   this.userMessage = '';
  // }

//   toggleChat() {
//     this.chatVisible = !this.chatVisible;
//     const chatContainer = this.el.nativeElement.querySelector('#chat-container');
//     this.chatVisible ? this.renderer.setStyle(chatContainer, 'display', 'block') : this.renderer.setStyle(chatContainer, 'display', 'none');
//   }
// }
}
