#include<iostream>
using namespace std;

int partition(int arr[], int st, int end){
    int idx=st-1;
    int pivot=arr[end];
    for(int i=st; i<end; i++){
        if(arr[i]<pivot){
            idx++;
            swap(arr[idx],arr[i]);
        }
    }
    swap(arr[idx+1], arr[end]);
    return idx+1;
}

void quickSort(int arr[], int st, int end){
    if(st<end){
        int p=partition(arr, st, end);
            quickSort(arr, st, p-1);
            quickSort(arr, p+1, end);
    }
}

int main(){
    int n;
    cin>>n;
    int arr[n];
    for(int i=0; i<n; i++){
        cin>>arr[i];
    }
    quickSort(arr, 0, n-1);
    for(int i=0; i<n; i++){
        cout<<arr[i]<<" ";
    }
}