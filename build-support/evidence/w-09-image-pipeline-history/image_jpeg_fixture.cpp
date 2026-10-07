#include <cstdio>
#include <cstdlib>
#include <jpeglib.h>
int main(int argc,char** argv){if(argc!=3)return 2;FILE* file=std::fopen(argv[1],"wb");if(!file)return 3;
    jpeg_compress_struct c{};jpeg_error_mgr error{};c.err=jpeg_std_error(&error);jpeg_create_compress(&c);jpeg_stdio_dest(&c,file);
    c.image_width=32;c.image_height=16;c.input_components=1;c.in_color_space=JCS_GRAYSCALE;jpeg_set_defaults(&c);jpeg_set_quality(&c,100,TRUE);
    if(argv[2][0]=='p')jpeg_simple_progression(&c);
    jpeg_start_compress(&c,TRUE);unsigned char row[32];
    while(c.next_scanline<c.image_height){for(unsigned x=0;x<32;++x)row[x]=static_cast<unsigned char>(32+(x/8)*48+(c.next_scanline/8)*16);JSAMPROW pointer=row;jpeg_write_scanlines(&c,&pointer,1);}
    jpeg_finish_compress(&c);jpeg_destroy_compress(&c);std::fclose(file);return 0;}
