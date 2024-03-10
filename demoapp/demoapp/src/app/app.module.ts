import { NgModule } from '@angular/core';
import { BrowserModule, HammerModule, HammerGestureConfig, HAMMER_GESTURE_CONFIG } from '@angular/platform-browser';
import { AppComponent } from './app.component';
import { HttpClientModule } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { ContentManagementComponent } from './content-management/content-management.component';
import { MatSliderModule } from '@angular/material/slider';
import { BrowserAnimationsModule } from '@angular/platform-browser/animations';
import { NotifierModule, NotifierOptions } from 'node_modules/angular-notifier';
import { ToastrModule } from 'ngx-toastr';

// Custom configuration for Notifier
const customNotifierOptions: NotifierOptions = {
  animations: {
    enabled: false,
    show: {
      preset: 'slide',
      speed: 300,
      easing: 'ease'
    },
    hide: {
      preset: 'fade',
      speed: 300,
      easing: 'ease',
      offset: 50
    },
    shift: {
      speed: 300,
      easing: 'ease'
    },
    overlap: false
  },
  behaviour: {
    autoHide: 1500,
    onClick: 'hide',
    onMouseover: 'pauseAutoHide',
    showDismissButton: true,
    stacking: 4
  },
  position: {
    horizontal: {
      position: 'right',
      distance: 12
    },
    vertical: {
      position: 'top',
      distance: 12,
      gap: 10
    }
  },
  theme: 'material'
  // templates: {
  //   // add your custom templates here
  // }
};

@NgModule({
  declarations: [
    AppComponent,
    ContentManagementComponent
  ],
  // Import necessary modules
  imports: [
    NotifierModule.withConfig(customNotifierOptions),
    HttpClientModule,
    BrowserModule,
    FormsModule,
    MatSliderModule,
    HammerModule,
    BrowserAnimationsModule,
    ToastrModule.forRoot({
      timeOut: 2000,
      positionClass: 'toast-bottom-right',
      preventDuplicates: true,
    })

  ],
  // Provide services
  providers: [
    { provide: HAMMER_GESTURE_CONFIG,
    useClass: HammerGestureConfig }
  ],
  // Launch AppComponent
  bootstrap: [AppComponent],
})
export class AppModule { }
