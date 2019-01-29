#include "ASHRAE205_generated.h"

#include <cstdio>

int main (int, char *argv[]) {
  FILE* file = fopen(argv[1],"rb");
  fseek(file, 0L, SEEK_END);
  int length = ftell(file);
  fseek(file, 0L, SEEK_SET);
  char *buf = new char[length];
  fread(buf, sizeof(char), length, file);
  fclose(file);

  auto chiller = GetASHRAE205(buf);

  printf("Equipment Type: %s\n", chiller->RSTitle()->c_str());

  printf("Representation Specification Version: %s\n", chiller->RSVersion()->c_str());

  printf("Equipment Description: %s\n", chiller->description()->c_str());

  auto rs = static_cast<const RS0001::RS0001_Root*>(chiller->RSInstance());

  auto gd = rs->GeneralDataTable();

  auto ahri = rs->AHRIRatingsTable();

  printf("  Manufacturer: %s\n", gd->manufacturer()->c_str());

  printf("  Compressor Type: %s\n", EnumNamesCompressorType()[gd->compressorType()]);

  printf("  COP: %.2f\n", ahri->designCOP());

  printf("  IPLV: %.1f\n", ahri->designPartLoadValue());

  return 0;
}
